"""Dashboard blueprint generator: problem -> layout, layers, palettes, widgets, rules."""
import json
import re
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from core import DATA_DIR, get_by_id, load_rows, parse_kv, search, split_list  # noqa: E402
from schema import INTENSITY_ORDER, MAP_CORNERS  # noqa: E402

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
INTENSITY_AUDIENCE = {"subtle": "public/civic audience", "balanced": "ops and analyst tools",
                      "bold": "pre-sales, story, events"}
BASELINE_FALLBACK = "civic-paper"
_TOKEN_COLS = ("basemap_recipe", "surface_recipe", "motion_recipe", "marker_grammar")


class UnknownDirection(ValueError):
    pass


# Screen spec: what every map screen must show in each whole-screen state (rule ids in brackets).
SCREEN_STATES = [
    {"state": "First load", "shows": "Restore the view from the URL; skeleton panels after ~1 s, "
                                      "map frame and controls visible at once [I08, P04]"},
    {"state": "No results", "shows": "Map stays; the list or panel says nothing matches and offers "
                                     "'clear filters'; active filters stay visible [I09]"},
    {"state": "Layer error", "shows": "Only the failed layer shows an error and retry in the layer panel; "
                                      "the rest of the screen keeps working [P06]"},
    {"state": "Stale or offline", "shows": "Freshness/status shows last update (and unsynced edits in the "
                                           "field); stale data is marked, not hidden [D02]"},
    {"state": "Feature selected", "shows": "Highlight on the map, details in the drawer or sheet, "
                                           "selection in the URL; Esc or back clears it [I08, A02]"},
]
MAP_CONTROLS = [
    "Top-right: zoom, compass (only if rotation), locate, fullscreen [C04, C05, C07]",
    "Top-left: search or coordinate entry (or in the header) [C04, C09]",
    "Bottom-left: scale bar [C04]; bottom edge: attribution, never covered [C01, L11]",
    "Legend: one entry per drawn class or state, synced with visible layers; bottom-left above the "
    "scale bar unless a panel holds it; on phones keep it above the sheet's peek height [S14, L09]",
]
# Where desktop-only regions go on phones when the layout's mobile_slots do not list them.
MOBILE_FALLBACK = {"panel": "sheet", "list": "sheet", "filters": "sheet", "drawer": "sheet",
                   "charts": "sheet", "action-bar": "sheet", "narrative": "sheet",
                   "kpi-strip": "sheet", "timeline": "sheet", "delta-strip": "sheet",
                   "status-bar": "sheet", "ticker": "sheet"}
PHONE_CATCHALL = ("sheet", "panel", "list", "charts", "narrative")


# Content regions tried, in order, when none of a widget's preferred slots exists in the layout.
CONTENT_FALLBACK = ("panel", "drawer", "list", "charts", "sheet", "narrative", "filters", "header")


def _slot_rows(cell):
    rows = []
    for name, spec in parse_kv(cell):
        position, _, size = spec.partition(",")
        rows.append({"slot": name, "position": position.strip(), "size": size.strip(), "widgets": []})
    return rows


def _with_corners(rows):
    if any(r["slot"] == "map" for r in rows):
        have = {r["slot"] for r in rows}
        rows += [{"slot": c, "position": c[4:].replace("-", " "), "size": "", "widgets": []}
                 for c in MAP_CORNERS if c not in have]
    return rows


def build_screen(layout, widgets):
    """Place the blueprint's widgets into the layout's named regions (desktop and mobile)."""
    if not layout:
        return None
    desk = _with_corners(_slot_rows(layout.get("slots", "")))
    mob = _with_corners(_slot_rows(layout.get("mobile_slots", "")))
    by_desk, by_mob = {r["slot"]: r for r in desk}, {r["slot"]: r for r in mob}
    unplaced, phone_unplaced, seen = [], [], set()
    for w in widgets:
        wd = w.get("widget")
        if not wd or wd.get("id", wd["name"]) in seen:
            continue
        seen.add(wd.get("id", wd["name"]))
        slot = next((s for s in split_list(wd.get("slot", "")) if s in by_desk), None)
        label = wd["name"]
        if not slot:
            slot = next((s for s in CONTENT_FALLBACK if s in by_desk), None)
            label += " (fallback)"
        if not slot:
            unplaced.append(wd["name"])
            continue
        by_desk[slot]["widgets"].append(label)
        if not by_mob:
            continue
        target = slot if slot in by_mob else MOBILE_FALLBACK.get(slot)
        if target not in by_mob:
            target = next((s for s in PHONE_CATCHALL if s in by_mob), None)
        if target:
            by_mob[target]["widgets"].append(label)
        else:
            phone_unplaced.append(label)
    keep = lambda rows: [r for r in rows if r["size"] or r["widgets"] or r["slot"] not in MAP_CORNERS]
    return {"slots": keep(desk), "mobile": keep(mob), "unplaced": unplaced, "phone_unplaced": phone_unplaced,
            "map_controls": MAP_CONTROLS, "states": SCREEN_STATES}


def build_signature(problem, data_dir=DATA_DIR, intensity=None, direction_id=None):
    ids = list(dict.fromkeys(split_list(problem.get("direction_ids", ""))))
    rows = [r for r in (get_by_id("direction", i, data_dir) for i in ids) if r]
    forced = None
    if direction_id:
        forced = get_by_id("direction", direction_id, data_dir)
        if not forced:
            raise UnknownDirection(f"Unknown direction {direction_id!r}")
        rows = [forced] + [r for r in rows if r["id"] != forced["id"]]
    if not rows:
        return None
    source = "override" if intensity else "problem"
    reason = "override via --intensity"
    if not intensity:
        intensity = problem.get("intensity_default", "")
        if intensity not in INTENSITY_ORDER:
            intensity = "balanced"
        reason = f"default for {problem.get('id', 'problem')}: {INTENSITY_AUDIENCE[intensity]}"
    idx = INTENSITY_ORDER.index

    def supports(r):
        return intensity in split_list(r["intensity_range"])

    def used(r):  # intensity in r's range nearest to the requested one
        rng = [x for x in split_list(r["intensity_range"]) if x in INTENSITY_ORDER]
        return min(rng, key=lambda x: abs(idx(x) - idx(intensity)), default=None)

    def dist(r):
        u = used(r)
        return abs(idx(u) - idx(intensity)) if u else len(INTENSITY_ORDER)
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
    chosen_ids = {r["id"] for r in chosen}
    base = next((r for r in rows if r["id"] not in chosen_ids
                 and "subtle" in split_list(r["intensity_range"])), None)
    if not base and BASELINE_FALLBACK not in chosen_ids:
        base = get_by_id("direction", BASELINE_FALLBACK, data_dir)
    stripped = not base
    base = base or top
    tokens = [[f"{c.split('_')[0]}.{k}" if k else c.split("_")[0], v]
              for c in _TOKEN_COLS for k, v in parse_kv(top[c])]
    tokens += [["type_pair", top["type_pair"]], ["accent_strategy", top["accent_strategy"]]]
    return {"intensity": intensity, "intensity_source": source, "intensity_reason": reason,
            "directions": chosen,
            "fallback_note": note,
            "baseline": {"id": base["id"], "name": base["name"], "intensity": "subtle",
                         "stripped": stripped},
            "locked": LOCKED_BASE, "direction_keeps": split_list(top["locked"]), "tokens": tokens,
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
        exact = get_by_id("widget", item, data_dir)  # an item may name a widget id directly
        h = [exact] if exact else search(item, "widget", 1, data_dir)["hits"]
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
            "rules": rules, "checklist": checklist, "signature": signature,
            "screen": build_screen(layout, widgets)}


def _slot_table(rows):
    out = ["| Region | Position | Size | Contains |", "|---|---|---|---|"]
    out += [f"| {r['slot']} | {r['position'] or '-'} | {r['size'] or '-'} | "
            f"{', '.join(r['widgets']) or '-'} |" for r in rows]
    return out


def _render_screen(screen):
    if not screen:
        return ["- (no layout)"]
    out = ["Desktop (1024 px and wider):", *_slot_table(screen["slots"])]
    if screen["unplaced"]:
        out.append(f"- Not placed by the layout (choose a region): {', '.join(screen['unplaced'])}")
    out += ["", "Map controls:", *[f"- {c}" for c in screen["map_controls"]], ""]
    out += ["Tablet (768-1023 px): keep the desktop regions; side panels shrink to their minimum "
            "width or become overlay drawers.", ""]
    out += (["Phone (under 768 px) [L09]:", *_slot_table(screen["mobile"])]
            if screen["mobile"] else ["Phone: see the layout's mobile note above [L09]"])
    if screen.get("phone_unplaced"):
        out.append(f"- No phone region for: {', '.join(screen['phone_unplaced'])} (choose one)")
    out += ["", "Screen states:", "| State | What the screen shows |", "|---|---|",
            *[f"| {s['state']} | {s['shows']} |" for s in screen["states"]]]
    return out


def _group_tokens(tokens):
    groups = {}
    for k, v in tokens:
        g, _, sub = k.partition(".")
        groups.setdefault(g, []).append(f"{sub}: {v}" if sub else v)
    return [(g, "; ".join(vs)) for g, vs in groups.items()]


def _render_signature(sig):
    if not sig:
        return ["- (no directions linked)"]
    out = [f"- Intensity: **{sig['intensity']}** ({sig['intensity_reason']})"]
    out += [f"- {'Primary' if i == 0 else 'Alternative'}: **{d['name']}** [{d['id']}] - {d['mood']}"
            for i, d in enumerate(sig["directions"])]
    if sig["fallback_note"]:
        out.append(f"- Note: {sig['fallback_note']}")
    b = sig["baseline"]
    if b and b.get("stripped"):
        out.append(f"- Safe baseline: {b['name']} with signature removed "
                   "(locked conventions, default markers, no hero)")
    else:
        out.append(f"- Safe baseline: {b['name']} [{b['id']}] (subtle)")
    out += ["", "### Locked conventions", *[f"- {x}" for x in sig["locked"]],
            *(["", "### Direction must-keeps", *[f"- {x}" for x in sig["direction_keeps"]]]
              if sig["direction_keeps"] else []),
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
    out += ["", "## Screen spec", *_render_screen(bp.get("screen"))]
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
    if args.direction:
        ids = [r["id"] for r in load_rows("direction", args.data_dir)]
        if args.direction not in ids:
            print(f"Unknown direction {args.direction!r}. Available: {', '.join(ids)}", file=sys.stderr)
            return 2
    bp = build_blueprint(args.query, args.data_dir, args.intensity, args.direction)
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
