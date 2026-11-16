---
name: gis-ui-ux-pro
description: GIS and remote-sensing UI/UX design intelligence for map screens - map layouts, layer panels, legends, color ramps, time sliders and before/after compare, EO imagery display, map accessibility and attribution, per-problem dashboard blueprints (vessel detection, flood, InSAR, deforestation, wildfire, fleet tracking, city service requests, parcel registry, data catalogs and more) and distinct-but-familiar signature directions for the map side (basemap tone, panels, motion, hero element) at subtle, balanced or bold intensity. Use when designing, building or reviewing the UI of web maps, GIS dashboards, WebGIS or Earth-observation apps (mapbox-gl, MapLibre, Leaflet, OpenLayers, deck.gl, Cesium, OGC WMS/WFS clients), choosing symbology and palettes for map data, or giving a map product its own visual direction. Not for calling GIS or EO platform APIs, data processing, tiling pipelines, logos or brand identity, or generic non-map UI styling.
---

# GIS UI/UX Pro

Work like a UI/UX designer for map products: ask what matters, ground every choice in the knowledge base, offer distinct directions with a safe fallback, and critique your own work before delivering. The knowledge base holds 122 rules, 28 problem playbooks, 33 palettes, 30 widgets, 9 layouts, 12 signature directions and 6 stack guides. The search script is the entry point; the two reference files are generated from the same data.

## When to apply

Apply when the work touches the **map surface or what sits around it**:

- Designing a new GIS dashboard, WebGIS app or EO viewer ("design a flood dashboard", "311 requests map for residents").
- Choosing symbology: color ramps, class breaks, legends, no-data and uncertainty encoding.
- Layer panels, basemaps, time sliders, swipe/compare, AOI drawing, popups, alert lists linked to the map.
- Giving a map product its own look ("make it feel less generic", "a signature for our fleet screen").
- Reviewing or auditing an existing map screen (code or screenshot).
- Library-specific map UI in mapbox-gl / MapLibre, Leaflet, OpenLayers, deck.gl, Cesium, or OGC service clients.

**Hand off** generic styling (fonts outside the map, brand system, buttons, forms, general page accessibility) to `ui-ux-pro-max` or `impeccable` if installed. Use both when a screen needs both.

**With ui-ux-pro-max:** it owns the app shell (type scale, buttons, forms, brand colours); this skill owns the map region and the panels that explain it, and wins on conflict there: no glass or blur over the map (A14), brand colours never encode data (S19), map motion follows the direction's motion recipe and reduced motion (A13). Map its dials to intensity: subtle ≈ `--variance 1-3 --motion 1-3`, balanced ≈ `4-7`, bold ≈ `8-10`; use `--density 8+` for ops screens.

**Do not apply** to operating a GIS/EO platform through its API, backend processing, tiling pipelines, or logo/brand identity work.

## Rule priority

When rules compete or time is short, satisfy categories in this order. Every `critical` rule sits in categories 1-3.

| # | Category (`category` in rules.csv) | Covers | Rule ids |
|---|---|---|---|
| 1 | `accessibility` - Accessibility & legibility | Text alternative, keyboard, no color-only meaning, contrast, focus, reduced motion | A.. |
| 2 | `controls` - Map chrome & attribution | Attribution, logo, control corners, scale bar, search/coordinate entry, basemap switcher | C.. |
| 3 | `symbology` - Symbology & legend | Normalized choropleths, classes, CVD-safe ramps, clustering, legends | S.. |
| 4 | `layers` - Layers | Purposeful layers, visible scale range, layer order, opacity, grouping | Y.. |
| 5 | `interaction` - Interaction | Hover vs click, popups, linked brushing, active filters, safe popup HTML, PII | I.. |
| 6 | `temporal` - Temporal | Compare modes, A/B date labels, time slider, UTC date filters | T.. |
| 7 | `eo` - EO specifics | Composite naming, fixed index ranges, SAR in dB, scene cards, detection confidence | E.. |
| 8 | `widgets` - Widgets | KPIs, freshness, uncertainty, alert lists, status workflows | D.. |
| 9 | `layout` - Layout | Map-first vs data-first, shell and action bar, mobile bottom sheet, z-order | L.. |
| 10 | `performance` - Performance | Vector tiles, slim GeoJSON, clustering, loading and error states | P.. |

Full rule list: [references/quick-reference.md](references/quick-reference.md). Audit checklist: [references/checklist.md](references/checklist.md).

## Running the script

Python 3 standard library only. Use `python`; if that fails, `python3`, then `py -3` (Windows). Always quote the script path.

```bash
python "${CLAUDE_SKILL_DIR}/scripts/search.py" "flood extent sentinel-1" --blueprint
python "${CLAUDE_SKILL_DIR}/scripts/search.py" "citizen service requests by ward" --blueprint --intensity subtle
python "${CLAUDE_SKILL_DIR}/scripts/search.py" "time slider" -d rule
python "${CLAUDE_SKILL_DIR}/scripts/search.py" "tracking replay scrubber" -d direction -n 2
python "${CLAUDE_SKILL_DIR}/scripts/search.py" "attribution control" -s leaflet -n 2
```

| Flag | Meaning |
|---|---|
| `-d rule\|problem\|palette\|widget\|layout\|direction` | Search one domain. Omit to auto-detect (falls back to `rule`). |
| `-s mapbox-maplibre\|leaflet\|openlayers\|deckgl\|cesium\|ogc` | Search one library's or service's stack guide instead of a domain. |
| `-n 1..20` | Number of results (default 3). |
| `--full` | Show full values (default output truncates long fields). |
| `--json` | Machine-readable output. |
| `--blueprint` | Match a problem description to a playbook and expand it into a dashboard blueprint, ending with a Signature section and the checklist. |
| `--intensity subtle\|balanced\|bold` | Blueprint only: override the problem's default intensity. |
| `--direction <id>` | Blueprint only: force a direction as primary. Unknown id exits 2 and lists the ids. |
| `-f markdown\|json` | Blueprint format (JSON includes a `signature` object). |
| `--persist -o DIR -p NAME` | Write `gis-design/<slug>/BLUEPRINT.md` under `DIR`. Refuses to overwrite unless `--force`. |

Exit codes: `0` for results and for "No matches" (which lists suggested keywords); `1` when `--blueprint` matches no problem (it prints the problem ids); `2` for argument errors, including `--intensity`/`--direction` without `--blueprint`.

### Evidence labels

Rules, problems, palettes and directions carry `evidence`:

- `sourced` - taken from the cited `source_url` (official docs, standards, published guidance). State it as established guidance and cite the URL when it matters.
- `synth` - synthesized guidance: a reasoned default, not a single-source fact. Present it as a recommended default, say so, and let the user override it.

Never present `synth` content as sourced, and never invent hex values when a palette exists in the data.

## Signature: distinct but familiar

Users trust maps that work like the maps they know (Jakob's law) and judge polished screens as easier to use (aesthetic-usability effect). So be most advanced yet acceptable: vary the look, never the conventions.

| Layer | What it holds | Rule |
|---|---|---|
| **Locked conventions** | Control positions, standard interactions and icons, CVD-safe data ramps from `palettes.csv`, attribution | Never varied |
| **Signature zones** | Basemap tone/recipe, panel shape and material, type pair, one accent, motion, marker/cluster grammar, exactly one hero element | Varied per product |
| **Intensity** | How far the signature zones move | Suggested by the problem, user overrides |

| Intensity | Audience | Feels like |
|---|---|---|
| `subtle` | Public and civic (residents, citizens, open data) | Quiet basemap, solid panels, near-instant motion, the hero element does the talking |
| `balanced` | Ops and analyst tools (control rooms, field, EO analysts) | Purposeful tone (dark ops, terrain, imagery-first), compact panels, one live accent |
| `bold` | Pre-sales, story, events, wall displays | Tilt, glow, editorial type, choreographed motion, still with a 2D and reduced-motion path |

**Hard rule (S19):** the signature never recolours data and never moves standard controls. Accents never reuse a data-ramp hue. Removing the signature must leave a fully usable app.

Map-specific constraints the directions already respect: the basemap recedes; dark basemaps are designed, not inverted, so no black halos on black (S20); text 4.5:1 and graphics 3:1 on the chosen basemap; `prefers-reduced-motion` means jumpTo instead of flyTo, crossfades, no looping animation, and a pause control for continuous motion (A13); glass/blur only over imagery-free areas with a reduce-transparency option (A14); 3D always ships with a 2D toggle; a command bar adds to, never replaces, a visible search box (I16).

## Workflow: design a new screen with a signature

**1. Discovery - at most 3 questions, only for what is unknown.** Check the user's message and the project (README, `package.json`, existing styles) first. Ask only what is still missing, from:

- Who uses it and where? (public web, office desk, field tablet, wall display)
- What feeling should it leave? (calm and trustworthy, fast and alert, impressive)
- Any brand constraints? (colors, fonts, an existing design system)

If the user wants speed, skip the questions and state your assumptions in the summary.

**2. Blueprint.** Run `--blueprint` with a one-line description in the user's words (sensor + target + purpose + audience). Check the matched problem and the runner-up; if the runner-up fits better, re-run with its terms. Add `--intensity` when discovery contradicts the problem's default (a public flood map is `subtle`; a pitch demo of the same data is `bold`). For 3D, pre-sales or story pitches pass `--intensity bold` and a fitting `--direction` (e.g. `urban-twin`, `newsroom-story`), since no playbook defaults to bold. The blueprint gives the layout with ASCII and mobile sketches, layers, palettes, widgets with states, temporal UI, interactions, alerts, pitfalls, then:

- **Screen spec:** a region table (region, position, size, which widgets it holds) for desktop and phone, the map-control corners and legend placement, and five whole-screen states (first load, no results, layer error, stale/offline, feature selected). Widgets marked "(fallback)" had no preferred region in this layout: decide where they go. Hand this table to developers as the screen description.
- **Signature:** intensity with its reason, primary and alternative directions, a safe `subtle` baseline that differs from both directions (a third linked direction, else Civic Paper, else "<Primary> with signature removed (locked conventions, default markers, no hero)"), locked conventions plus the primary direction's must-keeps, a token table for the primary (basemap, surface, motion, marker, type pair, accent), the hero element with one variation per axis, and a test plan (5-second, preference baseline vs primary, first-click, squint). A note appears when fewer than two directions fit the intensity or a forced direction is outside its range.
- **Pre-delivery checklist** with rule ids.

**3. Fill gaps** with one concern per query: `-d palette` for ramps, `-d widget` for states, `-d rule` for a behavior, `-d direction` for another look. Detect the map library from `package.json` or imports and run `-s <stack>` for what you will implement (attribution, layer order, clustering, picking, credits).

**4. Present two directions plus the safe baseline.** Short and contrasting, not three variants of the same thing. For each: one line of mood, what the user sees first, the hero element, and a small text sketch. Use the direction's `variation_axes` to make it this product's own (density, temperature, radius, tempo, hero variant) so two products never get identical output. Recommend one and say why in one sentence.

```text
A  Civic Paper (subtle)          B  Canvas Studio (subtle)        Baseline: Civic Paper
+--------------------------+     +--------------------------+     with signature removed
| [search]          [+][-] |     | [search] [tools]  [+][-] |     plain light basemap,
|  . .   .  light gray     |     |   soft strokes, sticky   |     solid panels, default
|    .  .   base, dots     |     |   note annotations       |     markers, no hero.
| "Each dot = one report,  |     | [sketch][note][share]    |     Ships if the signature is cut.
|  last 30 days"   [legend]|     |                 [legend] |
+--------------------------+     +--------------------------+
```

**5. Visual mock (optional, only when the user wants to see it).**

- If `impeccable` is installed, hand it the primary direction's token table and the locked conventions list; it builds the mock, this skill reviews the map side.
- Otherwise write one static HTML file: MapLibre GL JS from a CDN, OpenFreeMap as the keyless basemap (`https://tiles.openfreemap.org/styles/positron`, `.../liberty` or `.../bright`), restyled only through the direction's basemap recipe, plus the panels, legend and hero element with fake but plausible data. Keep MapLibre's attribution control visible; it must show "OpenFreeMap © OpenMapTiles Data from OpenStreetMap" with links to openfreemap.org, openmaptiles.org and openstreetmap.org/copyright (the OpenFreeMap part is optional, the OpenMapTiles and OpenStreetMap parts are not).
- Write the file into the user's project only when asked; otherwise show it or put it in a scratch location and say where.

**6. Self-critique before delivery.** Run the blueprint checklist plus any `critical` items in [references/checklist.md](references/checklist.md) that apply, then these signature checks. Report anything you could not meet.

- [ ] No locked convention changed (control corners, interactions, icons, attribution).
- [ ] Data ramps untouched: palette ids from the data, accent hue not in any ramp.
- [ ] Reduced-motion path specified (jumpTo, crossfade, pause control).
- [ ] Contrast checked on the chosen basemap: text 4.5:1, graphics 3:1, halos visible.
- [ ] Signature removable: the safe baseline still works with the same layout and data.

Use `--persist` only when the user wants the blueprint saved in their project.

### Output style

Lead with a 5-line summary, then details:

```text
Problem:   service-requests (runner-up data-catalog) - residents reporting city issues
Layout:    map-first with list drawer; bottom sheet on mobile
Direction: Civic Paper, subtle (alt Canvas Studio; baseline Civic Paper with signature removed)
Hero:      sentence legend "Each dot = one report, last 30 days"
Risks:     PII in popups (I11) - status by colour only (A07) - stale data without timestamp (D02)
```

Then: directions with sketches, the screen spec (regions, sizes, states), layers table (default on/off, symbology, palette hex), widgets with loading/empty/error/stale states, temporal UI, interactions, alert encoding, tokens, pitfalls, checklist. Cite rule ids (`S09`, `A07`). No repeated boilerplate: say each thing once, skip sections the blueprint already makes obvious.

## Workflow: reviewing an existing screen

1. Read the code (map init, layer definitions, legend, controls, popups) or the screenshot.
2. If the problem type is clear, run `--blueprint` for it so you know the expected layers, pitfalls and checklist.
3. Walk [references/checklist.md](references/checklist.md) group by group. Mark each item pass / fail / not applicable.
4. For each failure, look up the rule with `-d rule` (or `-s <stack>` for the fix in that library) to get do/don't and why.
5. If the user asks about the look, compare against the blueprint's directions and check the signature list above (a recoloured ramp or moved control is a finding, not a style choice).
6. Report findings ordered by severity (critical, high, medium, low). Each finding has: rule id, what you observed (file:line or screen region), why it matters, and the concrete fix.
7. Findings are defects in what the code or screen does. Accessibility (keyboard, text alternative, contrast, colour-only meaning), privacy, attribution and security gaps always stay in the severity-ordered findings, even when the feature is absent. Only optional features it never attempts (search, legend extras, table view) go last in an "Also consider (low, optional)" list, unless the user asked for a full audit.

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

Problem ids for `--blueprint` and `-d problem`: object-detection, maritime-awareness, land-change, surface-water-drought, flood, ground-deformation, wildfire, deforestation, oil-spill, crop-health, urban-planning, infrastructure-network, disaster-response, air-quality-heat, fleet-tracking, site-suitability, demographic-choropleth, real-estate, public-health, mining, coastal-erosion, crime-mapping, service-requests, asset-survey, parcel-registry, enforcement-casework, data-catalog, vegetation-cover-admin.

Direction ids for `--direction` and `-d direction`: civic-paper, field-atlas, night-ops, signal-track, orbital-lightbox, newsroom-story, canvas-studio, analytic-glow, living-atmosphere, conservation-signal, urban-twin, heritage-atlas.

## Worked example

User: "Design a vessel tracking screen for our ops room, using MapLibre. It shouldn't look like every other dark dashboard."

```bash
python "${CLAUDE_SKILL_DIR}/scripts/search.py" "vessel tracking ais ops" --blueprint
python "${CLAUDE_SKILL_DIR}/scripts/search.py" "vessel heading icon trail" -d direction -n 2
python "${CLAUDE_SKILL_DIR}/scripts/search.py" "alert list" -d widget -n 1
python "${CLAUDE_SKILL_DIR}/scripts/search.py" "attribution layer order" -s mapbox-maplibre
```

1. Audience (ops room) and library are known, so discovery asks two questions: the feeling (calm watch vs fast alerting) and any brand colors.
2. The blueprint suggests `balanced`, primary Signal Track (track replay scrubber as hero, type by shape before colour), alternative Night Ops (freshness strip with live/stale pulse), and Civic Paper as the safe baseline.
3. Present A and B with sketches, recommend Signal Track because replay answers the ops room's "what happened here" question; keep data colours from the blueprint's palettes.
4. Self-critique: attribution and logo visible (C01, C02), status not colour-only (A07), stale-data timestamp (D02), reduced-motion path for the scrubber playback, contrast of labels on the dark basemap, baseline still works.
