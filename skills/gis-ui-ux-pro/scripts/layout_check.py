#!/usr/bin/env python3
"""Measure a running map screen in a real browser and report layout defects.

Checks, per viewport: map controls and attribution covered or off screen
(C01, C02, L11, C04), floating panels overlapping each other (L11), text
smaller than --min-font, text cut off by its box, page-level horizontal
scroll, how much of the viewport the map keeps, and --expect texts (B10).
QA pass: --preset monitor --screenshot DIR --blur --cvd deuteranopia,achromatopsia
saves the blurred (B11) and colour-vision (A07) copies to look at.

Needs Playwright (optional; the rest of the skill is stdlib only):
    python -m pip install playwright && python -m playwright install chromium

Exit codes: 0 no high/medium findings, 1 high/medium findings, 2 bad
arguments, 3 Playwright missing, 4 page failed to load or a --click/--wait-for
selector was not found.
"""
import argparse
import json
import sys
from pathlib import Path

# ponytail: DOM-only. Labels drawn in the WebGL canvas and overlays with
# pointer-events:none are invisible to these checks; use screenshots for those.
PROBE = r"""
(opts) => {
  const VENDOR = /^(maplibregl|mapboxgl|leaflet|ol|cesium)-/;
  const MAP = '.maplibregl-map,.mapboxgl-map,.leaflet-container,.ol-viewport,.cesium-widget';
  const CTRL = '.maplibregl-ctrl,.mapboxgl-ctrl,.leaflet-control,.ol-control,.cesium-viewer-toolbar';
  const ATTR = '.maplibregl-ctrl-attrib,.mapboxgl-ctrl-attrib,.leaflet-control-attribution,.ol-attribution,.cesium-widget-credits';
  const W = innerWidth, H = innerHeight;
  const vis = el => {
    const r = el.getBoundingClientRect(), s = getComputedStyle(el);
    return r.width > 0 && r.height > 0 && s.visibility !== 'hidden' && s.display !== 'none' && +s.opacity > 0;
  };
  const inView = r => r.right > 0 && r.bottom > 0 && r.left < W && r.top < H;
  const name = el => el.id ? '#' + el.id : el.tagName.toLowerCase() +
    (typeof el.className === 'string' && el.className.trim()
      ? '.' + el.className.trim().split(/\s+/).slice(0, 2).join('.') : '');
  const path = el => { const p = []; for (let e = el; e && e !== document.body && p.length < 3; e = e.parentElement) p.unshift(name(e)); return p.join(' > '); };
  const vendor = el => { for (let e = el; e; e = e.parentElement) if ([...e.classList].some(c => VENDOR.test(c))) return true; return false; };
  const out = { viewport: [W, H], map: null, findings: [] };
  // The same message on many elements (a badge repeated in a list) is one finding with a count.
  const add = (rule, severity, message, el) => {
    const f = out.findings.find(x => x.rule === rule && x.message === message);
    if (f) f.count++;
    else out.findings.push({ rule, severity, message, element: el ? path(el) : '', count: 1 });
  };

  const map = [...document.querySelectorAll(MAP)].find(vis);
  if (map) {
    const r = map.getBoundingClientRect();
    out.map = { width: Math.round(r.width), height: Math.round(r.height), share: Math.round(100 * r.width * r.height / (W * H)) };
  } else add('-', 'info', 'No map container found (MapLibre, Mapbox, Leaflet, OpenLayers, Cesium)');

  // Topmost element at a few points of el; null when el itself is on top.
  const coveredBy = el => {
    const r = el.getBoundingClientRect();
    for (const fx of [0.5, 0.15, 0.85]) {
      const x = r.left + r.width * fx, y = r.top + r.height / 2;
      if (x < 0 || y < 0 || x >= W || y >= H) return 'off screen';
      const top = document.elementFromPoint(x, y);
      if (top && !el.contains(top) && !top.contains(el)) return top;
    }
    return null;
  };
  if (map) {
    const attr = [...document.querySelectorAll(ATTR)].filter(vis);
    if (!attr.length) add('C01', 'high', 'No visible attribution control on the map', map);
    for (const a of attr) {
      const c = coveredBy(a);
      if (c) add('C01', 'high', c === 'off screen' ? 'Attribution is off screen' : 'Attribution is covered by ' + path(c), a);
    }
    if (map.matches('.mapboxgl-map') && ![...document.querySelectorAll('.mapboxgl-ctrl-logo')].some(vis))
      add('C02', 'high', 'Mapbox logo is not visible', map);
    for (const c of [...document.querySelectorAll(CTRL)].filter(vis)) {
      if (c.matches(ATTR) || c.querySelector(ATTR)) continue;
      const by = coveredBy(c);
      if (by) add(by === 'off screen' ? 'C04' : 'L11', 'high',
        by === 'off screen' ? 'Map control is off screen' : 'Map control is covered by ' + path(by), c);
    }
  }

  // Outermost app-owned floating panels (absolute/fixed, at least 48x48, not map internals).
  // Smaller boxes are a component's own parts (slider thumbs, badges), stacked on purpose.
  const floats = [...document.body.querySelectorAll('*')].filter(el => {
    const p = getComputedStyle(el).position;
    if (p !== 'absolute' && p !== 'fixed') return false;
    const r = el.getBoundingClientRect();
    return r.width >= 48 && r.height >= 48 && inView(r) && vis(el) && !vendor(el);
  }).filter((el, _, all) => !all.some(o => o !== el && o.contains(el)));
  for (let i = 0; i < floats.length; i++) for (let j = i + 1; j < floats.length; j++) {
    const a = floats[i].getBoundingClientRect(), b = floats[j].getBoundingClientRect();
    const w = Math.min(a.right, b.right) - Math.max(a.left, b.left);
    const h = Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top);
    if (w > 2 && h > 2) add('L11', 'medium',
      `Overlaps ${path(floats[j])} by ${Math.round(w)}x${Math.round(h)} px (fine only if intended, e.g. a menu)`, floats[i]);
  }

  // Text size and clipping, one finding per element.
  const small = new Map(), clipped = new Set();
  const tw = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  for (let n = tw.nextNode(); n; n = tw.nextNode()) {
    const el = n.parentElement;
    if (!el || !n.textContent.trim() || !vis(el) || !inView(el.getBoundingClientRect())) continue;
    const s = getComputedStyle(el), fs = parseFloat(s.fontSize);
    if (fs < opts.minFont && !small.has(el) && !vendor(el)) small.set(el, fs); // the library's scale bar etc. are its own
    for (let e = el; e && e !== document.body; e = e.parentElement) {
      const o = getComputedStyle(e);
      if (o.overflowX !== 'visible' && o.whiteSpace === 'nowrap' && e.scrollWidth > e.clientWidth + 1) { clipped.add(e); break; }
    }
  }
  for (const [el, fs] of small) add('type', 'medium', `Text is ${fs}px, below ${opts.minFont}px: "${el.textContent.trim().slice(0, 40)}"`, el);
  for (const el of clipped) add('D10', 'low', `Text is cut off: "${el.textContent.trim().slice(0, 40)}"`, el);
  if (document.documentElement.scrollWidth > W + 1)
    add('L09', 'medium', `Page scrolls sideways: content is ${document.documentElement.scrollWidth}px wide`, null);
  return out;
}
"""

SEVERITY = ["high", "medium", "low", "info"]
# monitor: an ultrawide wall or desk, a laptop and a phone (B14 and the QA pass in SKILL.md)
PRESETS = {"monitor": "3440x1440,1440x900,375x812"}
CVD = ("protanopia", "deuteranopia", "tritanopia", "achromatopsia")
BLUR_CSS = "html{filter:blur(6px)!important}"

EXPECT_JS = r"""
([sel, want]) => {
  const norm = s => (s || '').replace(/\s+/g, ' ').trim();
  const els = [...document.querySelectorAll(sel)];
  if (!els.length) return 'missing';
  return els.some(e => norm(e.textContent).includes(norm(want))) ? 'ok' : els.map(e => norm(e.textContent)).join(' | ').slice(0, 120);
}
"""


def parse_size(s):
    try:
        w, h = (int(v) for v in s.lower().split("x"))
        return w, h
    except ValueError:
        raise argparse.ArgumentTypeError(f"size must be WIDTHxHEIGHT, got {s!r}")


def parse_sizes(s):
    return [parse_size(v) for v in s.split(",")]


def parse_expect(s):
    """'SELECTOR=TEXT' -> (selector, text); the '=' that splits is the first one after the selector's last ']'."""
    i = s.find("=", s.rfind("]") + 1)
    if i <= 0 or not s[:i].strip():
        raise argparse.ArgumentTypeError(f"expect must be SELECTOR=TEXT, got {s!r}")
    return s[:i].strip(), s[i + 1:]


def parse_cvd(s):
    out = [v.strip() for v in s.split(",") if v.strip()]
    bad = [v for v in out if v not in CVD]
    if bad or not out:
        raise argparse.ArgumentTypeError(f"unknown vision deficiency {', '.join(bad) or s!r}; use {', '.join(CVD)}")
    return out


def check_expect(page, expects):
    found = []
    for sel, want in expects:
        got = page.evaluate(EXPECT_JS, [sel, want])
        if got == "ok":
            continue
        msg = "Expected element not found" if got == "missing" else f"Expected text {want!r} missing (shows {got!r})"
        found.append({"severity": "high", "rule": "B10", "message": msg, "element": sel, "count": 1})
    return found


def extra_shots(page, base, blur, cvd):
    """Blurred copy (salience test, B11) and colour-vision copies (A07) of the current view."""
    out = []
    if blur:
        tag = page.add_style_tag(content=BLUR_CSS)
        out.append(f"{base}-blur.png")
        page.screenshot(path=out[-1])
        tag.evaluate("e => e.remove()")
    if cvd:
        cdp = page.context.new_cdp_session(page)
        for t in cvd:
            cdp.send("Emulation.setEmulatedVisionDeficiency", {"type": t})
            out.append(f"{base}-{t}.png")
            page.screenshot(path=out[-1])
        cdp.send("Emulation.setEmulatedVisionDeficiency", {"type": "none"})
    return out


def check(url, sizes, clicks, wait, wait_for, min_font, shots, settle, expects=(), blur=False, cvd=()):
    from playwright.sync_api import TimeoutError as PlaywrightTimeout, sync_playwright

    def calm(page):
        # Maps keep loading tiles and data after "load"; measuring early catches half-placed labels.
        if settle:
            try:
                page.wait_for_load_state("networkidle", timeout=settle)
            except PlaywrightTimeout:
                pass  # a live feed never goes idle: measure anyway after --wait
        page.wait_for_timeout(wait)

    reports = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        for w, h in sizes:
            page = browser.new_page(viewport={"width": w, "height": h})
            page.goto(url, wait_until="load")
            if wait_for:
                page.wait_for_selector(wait_for)
            calm(page)
            for sel in clicks:
                page.click(sel)
                calm(page)
            rep = page.evaluate(PROBE, {"minFont": min_font})
            rep["findings"] += check_expect(page, expects)
            rep["findings"].sort(key=lambda f: SEVERITY.index(f["severity"]))
            if shots:
                Path(shots).mkdir(parents=True, exist_ok=True)
                rep["screenshot"] = str(Path(shots) / f"layout-{w}x{h}.png")
                page.screenshot(path=rep["screenshot"])
                more = extra_shots(page, rep["screenshot"][:-4], blur, cvd)
                if more:
                    rep["extra_screenshots"] = more
            reports.append(rep)
            page.close()
        browser.close()
    return reports


def render(reports):
    lines = []
    for rep in reports:
        w, h = rep["viewport"]
        m = rep["map"]
        head = f"{w}x{h}  " + (f"map {m['width']}x{m['height']} ({m['share']}% of viewport)" if m else "no map")
        lines.append(head)
        for f in rep["findings"]:
            n = f" (x{f['count']})" if f["count"] > 1 else ""
            lines.append(f"  {f['severity']:<6} {f['rule']:<5} {f['message']}{n}" + (f"  [{f['element']}]" if f["element"] else ""))
        if not rep["findings"]:
            lines.append("  no findings")
        if rep.get("screenshot"):
            lines.append(f"  screenshot: {rep['screenshot']}")
        for p in rep.get("extra_screenshots") or []:
            lines.append(f"  screenshot: {p}")
    return "\n".join(lines)


def parse_args(argv=None):
    ap = argparse.ArgumentParser(description="Measure a map screen in a browser and report layout defects.")
    ap.add_argument("url", help="Page URL (http://, https:// or file://)")
    ap.add_argument("--sizes", default="1280x800,1440x900,1920x1080",
                    type=parse_sizes, help="Comma-separated WIDTHxHEIGHT list")
    ap.add_argument("--preset", choices=sorted(PRESETS),
                    help="Named size list instead of --sizes; monitor = " + PRESETS["monitor"])
    ap.add_argument("--expect", action="append", default=[], type=parse_expect, metavar="SELECTOR=TEXT",
                    help="Fail (B10) unless an element matching SELECTOR contains TEXT; repeatable, e.g. '#kpi-open=3'")
    ap.add_argument("--blur", action="store_true", help="With --screenshot: also save a blurred copy for the salience test (B11)")
    ap.add_argument("--cvd", type=parse_cvd, default=[], metavar="TYPES",
                    help="With --screenshot: also save copies under colour-vision emulation, e.g. deuteranopia,achromatopsia")
    ap.add_argument("--click", action="append", default=[], metavar="SELECTOR",
                    help="Click before measuring, e.g. to open a panel or chat (repeatable, in order)")
    ap.add_argument("--wait", type=int, default=1500, help="Extra milliseconds to wait after the page settles and after each click")
    ap.add_argument("--settle", type=int, default=15000,
                    help="Wait up to this many ms for the network to go idle before measuring (0 skips)")
    ap.add_argument("--wait-for", metavar="SELECTOR", help="Wait until this selector exists before measuring")
    ap.add_argument("--min-font", type=float, default=12, help="Smallest acceptable text size in px (default 12)")
    ap.add_argument("--screenshot", metavar="DIR", help="Save one screenshot per size into DIR")
    ap.add_argument("--json", action="store_true", help="Machine-readable output")
    args = ap.parse_args(argv)
    if args.preset:
        args.sizes = parse_sizes(PRESETS[args.preset])
    if (args.blur or args.cvd) and not args.screenshot:
        ap.error("--blur and --cvd need --screenshot DIR")
    return args


def main(argv=None):
    args = parse_args(argv)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    try:
        import playwright  # noqa: F401
    except ImportError:
        print("Playwright is not installed. Run:\n  python -m pip install playwright\n"
              "  python -m playwright install chromium", file=sys.stderr)
        return 3
    from playwright.sync_api import Error as PlaywrightError
    try:
        reports = check(args.url, args.sizes, args.click, args.wait, args.wait_for, args.min_font, args.screenshot, args.settle,
                        args.expect, args.blur, args.cvd)
    except PlaywrightError as e:
        print(f"Could not load or measure the page: {str(e).splitlines()[0]}", file=sys.stderr)
        return 4
    print(json.dumps(reports, indent=2) if args.json else render(reports))
    bad = any(f["severity"] in ("high", "medium") for r in reports for f in r["findings"])
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
