"""Dashboard blueprint generator: problem -> layout, layers, palettes, widgets, rules."""
import json
import re
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from core import DATA_DIR, get_by_id, load_rows, search, split_list  # noqa: E402

SEV_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}


def slug(project, fallback=""):
    text = unicodedata.normalize("NFKD", project.lower().replace("đ", "d"))
    text = "".join(c for c in text if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-") or fallback


def build_blueprint(description, data_dir=DATA_DIR):
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
            "rules": rules, "checklist": checklist}


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
    bp = build_blueprint(args.query, args.data_dir)
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
