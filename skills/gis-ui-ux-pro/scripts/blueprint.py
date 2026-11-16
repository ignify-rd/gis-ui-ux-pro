"""Dashboard blueprint generator: problem -> layout, layers, palettes, widgets, rules."""
import json
import re
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from core import DATA_DIR, get_by_id, load_rows, search, split_list  # noqa: E402
from schema import INTENSITY_ORDER  # noqa: E402

SEV_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}


def slug(project, fallback=""):
    text = unicodedata.normalize("NFKD", project.lower().replace("đ", "d"))
    text = "".join(c for c in text if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-") or fallback


LOCKED_BASE = ["Control positions (zoom, search, layers, legend) follow platform conventions",
               "Data colours come only from the listed palettes; the signature never recolours data",
               "Attribution stays visible",
               "Standard interactions: click opens details, drag pans, scroll or pinch zooms"]
TEST_PLAN = ["5-second test: show the map for 5 seconds; viewers should name its purpose and the main layer",
             "Preference test: show baseline vs top direction to 5+ users; ask which feels more trustworthy and easier to read",
             "First-click test: ask users to complete the key task; check the first click lands on the right control",
             "Squint test: blur the screen; the hero element and the data must still stand out"]
BASELINE_FALLBACK = "civic-paper"
_TOKEN_COLS = ("basemap_recipe", "surface_recipe", "motion_recipe", "marker_grammar")


def parse_kv(cell):
    out = []
    for item in cell.split(";"):
        item = item.strip()
        if item:
            k, sep, v = item.partition(":")
            out.append((k.strip(), v.strip()) if sep else ("", item))
    return out


def build_signature(problem, data_dir=DATA_DIR, intensity=None, direction_id=None):
    ids = list(dict.fromkeys(split_list(problem.get("direction_ids", ""))))
    rows = [r for r in (get_by_id("direction", i, data_dir) for i in ids) if r]
    forced = None
    if direction_id:
        forced = get_by_id("direction", direction_id, data_dir)
        if not forced:
            raise ValueError(f"Unknown direction {direction_id!r}")
        rows = [forced] + [r for r in rows if r["id"] != forced["id"]]
    if not rows:
        return None
    source = "override" if intensity else "problem"
    if not intensity:
        intensity = problem.get("intensity_default", "")
        if intensity not in INTENSITY_ORDER:
            intensity = "balanced"
    idx = INTENSITY_ORDER.index

    def supports(r):
        return intensity in split_list(r["intensity_range"])

    def used(r):  # intensity in r's range nearest to the requested one
        rng = [x for x in split_list(r["intensity_range"]) if x in INTENSITY_ORDER]
        return min(rng, key=lambda x: abs(idx(x) - idx(intensity)), default=None)

    def dist(r):
        u = used(r)
        return abs(idx(u) - idx(intensity)) if u else 9
    notes = []
    chosen = [r for r in rows if supports(r)]
    if forced and not supports(forced):
        chosen = [forced] + chosen
        notes.append(f"{forced['id']} is forced; its range ({forced['intensity_range']}) "
                     f"does not include {intensity}")
    chosen = chosen[:2]
    if len(chosen) < 2:
        rest = [r for r in rows if r not in chosen]  # stable sort keeps linked order on ties
        added = sorted(rest, key=dist)[:2 - len(chosen)]
        chosen += added
        if added:
            notes.append(f"Fewer than 2 directions support {intensity}; added nearest: "
                         + ", ".join(f"{r['id']} (at {used(r)})" for r in added))
    note = "; ".join(notes) or None
    top = chosen[0]
    base = next((r for r in rows if r is not top and "subtle" in split_list(r["intensity_range"])), None)
    if not base:
        cp = get_by_id("direction", BASELINE_FALLBACK, data_dir)
        base = cp if cp and cp["id"] != top["id"] else top
    same = base is top or base["id"] == top["id"]
    tokens = [[f"{c.split('_')[0]}.{k}" if k else c.split("_")[0], v]
              for c in _TOKEN_COLS for k, v in parse_kv(top[c])]
    tokens += [["type_pair", top["type_pair"]], ["accent_strategy", top["accent_strategy"]]]
    return {"intensity": intensity, "intensity_source": source, "directions": chosen,
            "fallback_note": note,
            "baseline": {"id": base["id"], "name": base["name"], "intensity": "subtle",
                         "same_as_primary": same},
            "locked": LOCKED_BASE + split_list(top["locked"]), "tokens": tokens,
            "hero_element": top["hero_element"],
            "variations": [[k, v] for k, v in parse_kv(top["variation_axes"])],
            "tests": TEST_PLAN}


def build_blueprint(description, data_dir=DATA_DIR, intensity=None, direction_id=None):
    hits = search(description, "problem", 2, data_dir)["hits"]
    if not hits:
        return None
    problem = {k: v for k, v in hits[0].items() if k != "_score"}
    layout = get_by_id("layout", problem["layout_id"], data_dir) if problem["layout_id"] else None
    palettes = [p for p in (get_by_id("palette", i, data_dir)
                            for i in split_list(problem["palette_ids"])) if p]
    widgets = []
    for item in split_list(problem["widgets"]):
        h = search(item, "widget", 1, data_dir)["hits"]
        widgets.append({"item": item,
                        "widget": {k: v for k, v in h[0].items() if k != "_score"} if h else None})
    signature = build_signature(problem, data_dir, intensity, direction_id)
    all_rules = load_rows("rule", data_dir)
    by_id = {r["id"]: r for r in all_rules}
    linked = [by_id[i] for i in split_list(problem["rule_ids"]) if i in by_id]
    rules = sorted((r for r in linked if r["severity"] in ("critical", "high")),
                   key=lambda r: SEV_ORDER[r["severity"]])
    checklist, seen = [], set()
    for r in linked + [r for r in all_rules if r["severity"] == "critical"]:
        if r["checklist"] and r["id"] not in seen:
            seen.add(r["id"])
            checklist.append({"rule_id": r["id"], "question": r["checklist"]})
    return {"problem": problem, "score": round(hits[0]["_score"], 2),
            "runner_up": hits[1]["id"] if len(hits) > 1 else None,
            "runner_up_score": round(hits[1]["_score"], 2) if len(hits) > 1 else None,
            "layout": layout, "palettes": palettes, "widgets": widgets,
            "rules": rules, "checklist": checklist, "signature": signature}


def _group_tokens(tokens):
    groups = {}
    for k, v in tokens:
        g, _, sub = k.partition(".")
        groups.setdefault(g, []).append(f"{sub}: {v}" if sub else v)
    return [(g, "; ".join(vs)) for g, vs in groups.items()]


def _render_signature(sig):
    if not sig:
        return ["- (no directions linked)"]
    out = [f"- Intensity: **{sig['intensity']}** ({sig['intensity_source']})"]
    out += [f"- {'Primary' if i == 0 else 'Alternative'}: **{d['name']}** [{d['id']}] - {d['mood']}"
            for i, d in enumerate(sig["directions"])]
    if sig["fallback_note"]:
        out.append(f"- Note: {sig['fallback_note']}")
    if sig["baseline"]:
        out.append(f"- Safe baseline: {sig['baseline']['name']} [{sig['baseline']['id']}] (subtle)"
                   + (" (same as primary)" if sig["baseline"].get("same_as_primary") else ""))
    out += ["", "### Locked conventions", *[f"- {x}" for x in sig["locked"]],
            "", "### Tokens (top direction)", "| Token | Value |", "|---|---|",
            *[f"| {g} | {v.replace('|', '/')} |" for g, v in _group_tokens(sig["tokens"])],
            "", "### Hero element", sig["hero_element"] or "n/a"]
    if sig["variations"]:
        out.append("Variations: " + "; ".join(f"{k}: {v}" for k, v in sig["variations"]))
    out += ["", "Test with users: 5-second \u00b7 preference (baseline vs primary) \u00b7 first-click \u00b7 squint"]
    return out


def _bullets(cell):
    return [f"- {x}" for x in split_list(cell)] or ["- (none)"]


def _syn(row):
    return " (synth)" if row.get("evidence") == "synth" else ""


def render_markdown(bp, project=None):
    p, lay = bp["problem"], bp["layout"]
    out = [f"# Dashboard Blueprint: {p['name']}"]
    if project:
        out.append(f"\nProject: {project}")
    out += ["", "## Matched problem", f"- **{p['name']}** [{p['id']}]{_syn(p)} (score {bp['score']})",
            "- Runner-up: " + (f"{bp['runner_up']} (score {bp['runner_up_score']})"
                              if bp["runner_up"] else "none"),
            "", "## Key user questions", *_bullets(p["user_questions"]), "", "## Layout"]
    if lay:
        out += [f"**{lay['name']}** [{lay['id']}]", f"- Regions: {lay['regions']}",
                f"- Mobile: {lay['mobile_variant'] or 'n/a'}", "", "```", lay["ascii_sketch"], "```"]
    else:
        out.append("- (none)")
    out += ["", "## Layers", "On by default:", *_bullets(p["layers_default_on"]),
            "Off by default:", *_bullets(p["layers_default_off"]),
            f"Symbology: {p['symbology'] or 'n/a'}", "", "## Palettes"]
    for pal in bp["palettes"]:
        out.append(f"- **{pal['name']}** [{pal['type']}]{_syn(pal)}: {pal['stops_hex']}"
                   f" | dark: {pal['dark_basemap_stops_hex'] or 'n/a'}"
                   f" | evidence: {pal['evidence']}")
    if not bp["palettes"]:
        out.append("- (none)")
    out += ["", "## Widgets"]
    for w in bp["widgets"]:
        wd = w["widget"]
        out.append(f"- {w['item']} → {wd['name']} (states: {wd['required_states']})"
                   if wd else f"- {w['item']} → (no widget match)")
    if not bp["widgets"]:
        out.append("- (none)")
    out += ["", "## Temporal", *_bullets(p["temporal"]), "", "## Interactions",
            *_bullets(p["interactions"]), "", "## Alerts & severity", *_bullets(p["alerts"]),
            "", "## Pitfalls", *_bullets(p["pitfalls"]), "", "## Rules to apply"]
    out += [f"- [{r['severity']}] {r['name']} ({r['id']}){_syn(r)}: {r['do']}" for r in bp["rules"]] \
        or ["- (none)"]
    out += ["", "## Signature", *_render_signature(bp.get("signature"))]
    out += ["", "## Pre-delivery checklist"]
    out += [f"- [ ] {c['question']} ({c['rule_id']})" for c in bp["checklist"]] or ["- (none)"]
    return "\n".join(out) + "\n"


def persist(markdown, out_dir, project, force=False, fallback=""):
    path = Path(out_dir) / "gis-design" / slug(project, fallback) / "BLUEPRINT.md"
    if path.exists() and not force:
        raise FileExistsError(str(path))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(markdown, encoding="utf-8")
    return path


def main_blueprint(args):
    try:
        bp = build_blueprint(args.query, args.data_dir, args.intensity, args.direction)
    except ValueError as e:
        ids = ", ".join(r["id"] for r in load_rows("direction", args.data_dir))
        print(f"{e}. Available: {ids}", file=sys.stderr)
        return 2
    if bp is None:
        ids = ", ".join(r["id"] for r in load_rows("problem", args.data_dir))
        print(f'No problem matched "{args.query}". Available: {ids}')
        return 1
    md = render_markdown(bp, args.project)
    if args.persist:
        try:
            path = persist(md, args.output_dir or ".", args.project or bp["problem"]["id"],
                           args.force, bp["problem"]["id"])
        except FileExistsError as e:
            print(f"BLUEPRINT.md exists at {e}; use --force", file=sys.stderr)
            return 1
        print(f"Saved {path}", file=sys.stderr)
    if args.format == "json":
        print(json.dumps(bp, ensure_ascii=False, indent=2))
    else:
        print(md)
    return 0
