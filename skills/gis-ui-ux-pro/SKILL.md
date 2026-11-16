---
name: gis-ui-ux-pro
description: GIS and remote-sensing UI/UX design intelligence for map screens - map layouts, layer panels, legends, color ramps, time sliders and before/after compare, EO imagery display, map accessibility and attribution, plus per-problem dashboard blueprints (vessel detection, flood, landslide/InSAR, deforestation, water change, wildfire, air quality, fleet tracking and more). Use when designing, building or reviewing the UI of web maps, GIS dashboards, WebGIS or Earth-observation apps (mapbox-gl, MapLibre, Leaflet, OpenLayers, deck.gl), or choosing symbology and palettes for map data. Not for calling GIS or EO platform APIs, data processing, tiling pipelines, or generic non-map UI styling.
---

# GIS UI/UX Pro

A searchable knowledge base for designing and reviewing map-centric web apps: 122 rules, 22 problem playbooks, 33 palettes, 22 widgets, 9 layouts and 4 map-library stack guides. The search script is the entry point; the two reference files are generated from the same data.

## When to apply

Apply when the work touches the **map surface or what sits around it**:

- Designing a new GIS dashboard, WebGIS app or EO viewer ("design a flood dashboard", "screen for Sentinel-1 vessel detection").
- Choosing symbology: color ramps, class breaks, legends, no-data and uncertainty encoding.
- Layer panels, basemaps, time sliders, swipe/compare, AOI drawing, popups, alert lists linked to the map.
- Reviewing or auditing an existing map screen (code or screenshot).
- Library-specific map UI in mapbox-gl / MapLibre, Leaflet, OpenLayers or deck.gl.

**Hand off** generic styling (fonts, brand colors, buttons, forms, general page accessibility) to `ui-ux-pro-max` or `impeccable` if installed. This skill does not duplicate them; use both when a screen needs both.

**Do not apply** to operating a GIS/EO platform through its API (for example creating a project or running a job), to backend processing, or to tiling pipelines.

## Rule priority

When rules compete or time is short, satisfy categories in this order. Every `critical` rule sits in categories 1-3.

| # | Category (`category` in rules.csv) | Covers | Rule ids |
|---|---|---|---|
| 1 | `accessibility` - Accessibility & legibility | Text alternative, keyboard, no color-only meaning, contrast, focus | A.. |
| 2 | `controls` - Map chrome & attribution | Attribution, logo, control corners, scale bar, search/coordinate entry, basemap switcher | C.. |
| 3 | `symbology` - Symbology & legend | Normalized choropleths, classes, CVD-safe ramps, clustering, legends | S.. |
| 4 | `layers` - Layers | Purposeful layers, visible scale range, layer order, opacity, grouping | Y.. |
| 5 | `interaction` - Interaction | Hover vs click, popups, linked brushing, active filters, URL view state | I.. |
| 6 | `temporal` - Temporal | Compare modes, A/B date labels, time slider, cloud-cover filters | T.. |
| 7 | `eo` - EO specifics | Composite naming, fixed index ranges, SAR in dB, scene cards, detection confidence | E.. |
| 8 | `widgets` - Widgets | KPIs, freshness, uncertainty, alert lists, shared palettes | D.. |
| 9 | `layout` - Layout | Map-first vs data-first, shell and action bar, mobile bottom sheet, z-order | L.. |
| 10 | `performance` - Performance | Vector tiles, slim GeoJSON, clustering, loading and error states | P.. |

Full rule list: [references/quick-reference.md](references/quick-reference.md). Audit checklist: [references/checklist.md](references/checklist.md).

## Running the script

The script is Python 3 standard library only. Use `python`; if that fails, try `python3`, then `py -3` (Windows launcher). Always quote the script path.

```bash
python "${CLAUDE_SKILL_DIR}/scripts/search.py" "flood extent sentinel-1" --blueprint
python "${CLAUDE_SKILL_DIR}/scripts/search.py" "time slider" -d rule
python "${CLAUDE_SKILL_DIR}/scripts/search.py" "attribution control" -s leaflet -n 2
```

| Flag | Meaning |
|---|---|
| `-d rule\|problem\|palette\|widget\|layout` | Search one domain. Omit to auto-detect (falls back to `rule`). |
| `-s mapbox-maplibre\|leaflet\|openlayers\|deckgl` | Search one library's stack guide instead of a domain. |
| `-n 1..20` | Number of results (default 3). |
| `--full` | Show full values (default output truncates long fields). |
| `--json` | Machine-readable output. |
| `--blueprint` | Match a problem description to a playbook and expand it into a dashboard blueprint. |
| `-f markdown\|json` | Blueprint format. |
| `--persist -o DIR -p NAME` | Write `gis-design/<slug>/BLUEPRINT.md` under `DIR`. Refuses to overwrite unless `--force`. |

Exit codes: `0` for results and for "No matches" (which lists suggested keywords); `1` when `--blueprint` matches no problem (it prints the available problem ids).

### Evidence labels

Rules, problems and palettes carry `evidence`:

- `sourced` - taken from the cited `source_url` (official docs, standards, published guidance). State it as established guidance and cite the URL when it matters.
- `synth` - synthesized guidance: a reasoned default, not a single-source fact (for example the flood/no-data palette or the fire-age ramp). Present it as a recommended default, say it is not from an authoritative source, and let the user override it.

Never present `synth` content as sourced, and never invent hex values when a palette exists in the data.

## Workflow: new screen or app

1. **Identify the problem type.** Run `--blueprint` with a one-line description in the user's words (sensor + target + purpose). Check the matched problem and the runner-up; if the runner-up fits better, re-run with that problem's terms.
2. **Take the layout** from the blueprint (it includes an ASCII sketch and a mobile variant). Search `-d layout` only if the user's context rules it out (wall display, mobile-first, story).
3. **Fill gaps with targeted searches.** One concern per query: `-d palette` for ramps, `-d widget` for a widget's required states, `-d rule` for a specific behavior.
4. **Add stack guidance.** Detect the map library from `package.json` or imports and run `-s <stack>` for the features you will implement (attribution, layer order, clustering, picking).
5. **Run the checklist** before delivering: the blueprint's "Pre-delivery checklist" section plus any `critical` items in [references/checklist.md](references/checklist.md) that apply. Report any item you could not meet.

Deliverable for a design request: layout sketch, layers table (default on/off, symbology, palette hex), widgets with their loading/empty/error/stale states, temporal UI, interactions, alert encoding, pitfalls, then the checklist. Cite rule ids (for example `S09`, `A07`).

Use `--persist` only when the user wants the blueprint saved in their project.

## Workflow: reviewing an existing screen

1. Read the code (map init, layer definitions, legend, controls) or the screenshot.
2. If the problem type is clear, run `--blueprint` for it so you know the expected layers, pitfalls and checklist.
3. Walk [references/checklist.md](references/checklist.md) group by group. Mark each item pass / fail / not applicable.
4. For each failure, look up the rule with `-d rule` (or `-s <stack>` for the fix in that library) to get do/don't and why.
5. Report findings ordered by severity (critical, high, medium, low). Each finding has: rule id, what you observed (file:line or screen region), why it matters, and the concrete fix.

Review checklist for yourself:

- [ ] Every finding cites a rule id or is labeled as general advice.
- [ ] Critical items (attribution, color-only meaning, keyboard, normalized choropleths) were checked explicitly.
- [ ] `synth` guidance is labeled as a default, not a requirement.

## Query contract

- **One intent per query**, 2-5 meaningful terms: `"legend hidden layers"`, not `"make the map look good and accessible"`.
- **Pass the domain or stack** when you know it; auto-detection is a fallback.
- **Verify the top result** (id, name, domain) actually answers the question before using it.
- **Retry once** with a narrower rewrite or explicit `-d`/`-s` if the output is "No matches" or off-topic. Use the suggested keywords it prints.
- **If the retry fails**, say no match was found and label your advice as general guidance, not from the knowledge base. Do not cycle through unrelated keywords.
- **Do not persist** a blueprint whose matched problem does not fit the user's problem.

Problem ids for `--blueprint` and `-d problem`: object-detection, maritime-awareness, land-change, surface-water-drought, flood, ground-deformation, wildfire, deforestation, oil-spill, crop-health, urban-planning, infrastructure-network, disaster-response, air-quality-heat, fleet-tracking, site-suitability, demographic-choropleth, real-estate, public-health, mining, coastal-erosion, crime-mapping.

## Worked example

User: "Design a dashboard for flood mapping from Sentinel-1, using MapLibre."

```bash
python "${CLAUDE_SKILL_DIR}/scripts/search.py" "flood mapping sentinel-1 exposure" --blueprint
python "${CLAUDE_SKILL_DIR}/scripts/search.py" "flood permanent water no-data" -d palette -n 2
python "${CLAUDE_SKILL_DIR}/scripts/search.py" "swipe compare" -d widget -n 1
python "${CLAUDE_SKILL_DIR}/scripts/search.py" "attribution layer order" -s mapbox-maplibre
```

1. The blueprint matches `flood` (runner-up shown for sanity). It gives the compare-split-view layout, layers on by default (observed flood, reference water, hatched no-data mask), off by default (likelihood, forecast, depth), and pitfalls such as "same blue for flood and permanent water".
2. The palette search returns the flood/water/no-data palette, labeled `synth`: present it as a default and say so.
3. The widget search gives swipe-compare's required states; the stack search gives the MapLibre attribution and layer-order details.
4. Deliver the blueprint sections, then the pre-delivery checklist (D02 freshness, T02 dates on both halves, S09 CVD-safe, A07 not color-only, C01 attribution, ...), noting which items the design already satisfies.
