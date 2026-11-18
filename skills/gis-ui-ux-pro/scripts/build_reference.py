"""Generate references/quick-reference.md and checklist.md from rules.csv and smells.csv."""
import argparse
import sys
from pathlib import Path

from core import DATA_DIR, SKILL_DIR, load_rows, split_list

ORDER = ["accessibility", "controls", "symbology", "layers", "interaction",
         "temporal", "eo", "widgets", "dashboard", "layout", "performance"]
SEV = ["critical", "high", "medium", "low"]
TITLES = {"eo": "EO"}


def _t(c):
    return TITLES.get(c, c.title())


def _one(s):
    return " ".join((s or "").split())


def _grouped(rows):
    cats = ORDER + sorted({r["category"] for r in rows} - set(ORDER))
    for c in cats:
        rs = [r for r in rows if r["category"] == c]
        if rs:
            yield c, rs


def _quick(rows):
    out = ["# GIS UI/UX Quick Reference", "",
           "Generated from `data/rules.csv` by `scripts/build_reference.py`. Do not edit by hand.",
           "", "## Contents", ""]
    groups = list(_grouped(rows))
    out += [f"- [{_t(c)}](#{_t(c).lower()})" for c, _ in groups]
    for c, rs in groups:
        out += ["", f"## {_t(c)}", ""]
        for r in rs:
            flag = r["severity"] + (", synth" if r["evidence"] == "synth" else "")
            line = (f"- **{r['id']} {_one(r['name'])}** ({flag}): "
                    f"Do: {_one(r['do'])} Don't: {_one(r['dont'])}")
            if r["source_url"].strip():
                line += f" [source]({r['source_url'].strip()})"
            out.append(line)
    return "\n".join(out) + "\n"


def _cell(s):
    return _one(s).replace("|", "\\|")


def _checklist(rows, smells=()):
    out = ["# GIS UI/UX Audit Checklist", "",
           "Generated from `data/rules.csv` and `data/smells.csv`. Tick each item while auditing a screen; "
           "critical items come first in each group.", ""]
    for c, rs in _grouped([r for r in rows if r["checklist"].strip()]):
        rs = sorted(rs, key=lambda r: SEV.index(r["severity"]) if r["severity"] in SEV else len(SEV))
        out += [f"## {_t(c)}", ""]
        out += [f"- [ ] {_one(r['checklist'])} ({r['id']}, {r['severity']})" for r in rs]
        out.append("")
    if smells:
        out += ["## Smells", "", "Spot the smell on the screen, then apply the fix; the rules hold the reason.", "",
                "| Smell | Instead | Rules |", "|---|---|---|"]
        out += [f"| {_cell(s['smell'])} | {_cell(s['instead'])} | {'; '.join(split_list(s['rule_ids']))} |"
                for s in smells]
        out.append("")
    return "\n".join(out).rstrip("\n") + "\n"


def _smells(data_dir):
    try:
        return load_rows("smell", data_dir)
    except FileNotFoundError:
        return []


def build(data_dir=DATA_DIR, ref_dir=SKILL_DIR / "references"):
    rows = load_rows("rule", data_dir)
    ref_dir = Path(ref_dir)
    ref_dir.mkdir(parents=True, exist_ok=True)
    q, c = ref_dir / "quick-reference.md", ref_dir / "checklist.md"
    for p, text in ((q, _quick(rows)), (c, _checklist(rows, _smells(data_dir)))):
        p.write_text(text, encoding="utf-8", newline="\n")
    return q, c


def _norm(p):
    return p.read_bytes().replace(b"\r\n", b"\n") if p.is_file() else None


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true", help="exit 1 if files on disk are stale")
    ap.add_argument("--data-dir", type=Path, default=DATA_DIR)
    ap.add_argument("--ref-dir", type=Path, default=SKILL_DIR / "references")
    a = ap.parse_args(argv)
    if not a.check:
        for p in build(a.data_dir, a.ref_dir):
            print(f"wrote {p}")
        return 0
    rows = load_rows("rule", a.data_dir)
    want = {"quick-reference.md": _quick(rows), "checklist.md": _checklist(rows, _smells(a.data_dir))}
    stale = [n for n, t in want.items() if _norm(a.ref_dir / n) != t.encode("utf-8")]
    for n in stale:
        print(f"stale: {n} (run build_reference.py)", file=sys.stderr)
    return 1 if stale else 0


if __name__ == "__main__":
    sys.exit(main())
