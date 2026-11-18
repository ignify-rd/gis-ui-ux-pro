## 0.4.0 - 2026-11-18

### Added

- Rules (141 total): B10 known totals checked per widget, B11 the eye lands on the problem, B12 wordless panels, B13 honest deltas, B14 the monitoring view fits one screen, B15 one word per concept, S21 intensity grows toward the problem, I17 action beside the flag, Y10 zoom tiers follow the monitoring sequence, D13 bullet graph instead of a gauge.
- Widgets (37 total): bullet-graph, segmented-share-bar, sparkline.
- Smell domain: `data/smells.csv` (24 rows: smell, fix, rule ids), `-d smell`, auto-detected on "smell" or "anti pattern", validated rule ids, and a Smells table at the end of `references/checklist.md`.
- `layout_check.py`: `--preset monitor` (3440x1440, 1440x900, 375x812), `--blur` and `--cvd` extra screenshots, `--expect SELECTOR=TEXT` (high B10 finding when missing). Defaults unchanged.
- SKILL.md: the design workflow makes the contract concrete (numbers, numeric problem rules, actions, a fixture with expected answers, zoom tiers); a pre-delivery QA step (known totals, words audit, salience, monitor shots, smells); reviews open with a verdict and what works, and order findings within a severity by honesty, then salience, hierarchy, words, smells, polish.

### Changed

- D01 points to B13, B05 to B10; kpi-tile cites B12/B13, calendar-heatmap S21.
- Plugin and marketplace version 0.4.0.

Ideas for the honesty and salience checks come from the MIT-licensed dashboard-design skill; the rules here are written for map screens in our own words and cite primary sources where they state the rule.

## 0.3.0 - 2026-11-17

### Added

- Dashboard contract: `problems.csv` columns `glance_question`, `glance_answer`, `trust`, `flow`, filled for all 30 problems (synth). The blueprint renders `## Dashboard contract (synth default)` after Key user questions; JSON blueprints gain a `contract` object. The validator checks the contract (widget references resolve, cited rule ids exist and link back, formats).
- Rule category `dashboard` with B01-B09: one primary question per screen, precision, readable time axes, one unit across the screen, numbers that reconcile, measured vs estimated vs forecast, back keeps place, feedback names its subject, review before publish. The T08 checklist is filled.
- Widgets (34 total): calendar-heatmap, detection-inspector, value-marker, aoi-summary-card. `availability-date-picker` shows per-date counts and a compare date.
- Problems (30 total): hazard-site-screening, weather-monitoring.
- SKILL.md: rule priority row 9 `dashboard`; design workflow step 2 presents the contract first; the review workflow compares the screen's actual glance, trust and flow with the contract before the checklist.

### Changed

- D09 applies to any list; I04 covers tooltips.
- Keyword fixes: VHR ship detection matches object-detection, drinking-water lakes match surface-water-drought. The relevance test supports `top1` and `min_margin`.
- Review workflow: cite a B rule only when the screen visibly shows the defect; B05-B08 state when they apply. S05 covers binning a continuous index into named classes (very low to very high) without stating method and breaks.
- Plugin and marketplace version 0.3.0.

## 0.2.3 - 2026-11-17

### Changed

- `layout_check.py` is quieter on real apps: it waits for the network to go idle before measuring (`--settle MS`, default 15000, `0` skips), so labels are measured after the map has placed them; only floating boxes of at least 48x48 px count as panels for overlap (slider thumbs and badges no longer report); text inside the map library's own controls (scale bar) is not flagged for size; a message repeated on many elements is one finding with a count (`count` in JSON, `(xN)` in text).

## 0.2.2 - 2026-11-17

### Added

- `scripts/layout_check.py` (optional, needs Playwright): opens a running map screen at several widths, optionally clicks to open panels, and reports attribution or map controls covered or off screen (C01, C02, L11, C04), overlapping floating panels (L11), text below `--min-font`, cut-off text (D10), sideways page scroll and the map's share of the viewport. Text or JSON output, optional screenshots. The review workflow in SKILL.md runs it when the app is running locally.

## 0.2.1 - 2026-11-16

### Added

- Blueprint "Screen spec" section after Widgets: a region table (region, position, size, widgets it holds) for desktop and phone, map-control corners and legend placement, and five whole-screen states (first load, no results, layer error, stale/offline, feature selected) with rule ids. JSON blueprints gain a `screen` object.
- `layouts.csv` columns `slots` and `mobile_slots` (`region: position, size`); `widgets.csv` column `slot` (preferred regions in order). Widgets with no preferred region in a layout go to the first content region and are marked "(fallback)"; on phones, regions the layout lacks fall back to the sheet, panel, list, charts or narrative, and anything left is listed as "No phone region for". A tablet line (768-1023 px) and a legend-above-the-sheet rule are included. The validator rejects unknown region names; a test checks every playbook places all its widgets on desktop and phone.
- SKILL.md: how to work with ui-ux-pro-max (who owns the shell vs the map region, conflict rules, intensity ↔ variance/motion/density dial mapping).

### Changed

- A problem's `widgets` item that is an exact widget id now resolves to that widget before BM25 search.
- `parse_kv` moved to `core.py` (still importable from `blueprint`).

## 0.2.0 - 2026-11-16

### Added

- Map signature system: `data/directions.csv` with 12 directions (civic-paper, field-atlas, night-ops, signal-track, orbital-lightbox, newsroom-story, canvas-studio, analytic-glow, living-atmosphere, conservation-signal, urban-twin, heritage-atlas), each with basemap/surface/motion/marker recipes, an open-licensed type pair, one hero element, locked conventions, variation axes and pitfalls. Directions reference palette ids only and never define data ramps.
- `-d direction` domain; `--intensity subtle|balanced|bold` and `--direction <id>` for `--blueprint` (exit 2 without `--blueprint`; an unknown direction exits 2 and lists the ids).
- Blueprint "Signature" section before the checklist: audience and intensity with the reason (default for the problem with its audience, or override), two directions plus a safe `subtle` baseline that differs from both (or the primary with its signature removed), locked conventions with the direction's own must-keeps under a separate heading, token table, hero element with variations, and a user-test plan. JSON blueprints gain a `signature` object (`intensity_reason`, `locked`, `direction_keeps`).
- Validator: every direction `intensity_range` must be contiguous in subtle, balanced, bold.
- `problems.csv` columns `direction_ids` and `intensity_default`; 6 new playbooks: service-requests, asset-survey, parcel-registry, enforcement-casework, data-catalog, vegetation-cover-admin (28 problems).
- 19 new rules (122 total), including UTC time filters (T10), popups as text not HTML (I10), personal data by role (I11), export map elements (D11), case workflow with audit (D12), reduced motion for the camera (A13), glass panels (A14), signature never changes data encoding (S19), designed dark basemaps (S20) and command bar beside search (I16).
- 8 new widgets (30 total): data-import, raster-display, query-builder, admin-drilldown, feature-editor, case-workflow, sync-status, ai-command.
- Stack guides `-s cesium` (9 rows) and `-s ogc` (8 rows, WMS/WFS/WMTS clients).
- SKILL.md designer workflow: discovery (at most 3 questions), two directions plus a safe baseline with text sketches, optional visual mock (`impeccable` hand-off or a single MapLibre + OpenFreeMap HTML file with visible attribution), self-critique, and a 5-line summary output style.
- Trigger queries: 3 should-trigger (signature/visual direction for map apps) and 2 should-not-trigger (brand identity, marketing site theme).

### Changed

- Domain auto-detect now normalizes plurals (colors -> color, colormaps/palettes -> palette).
- `histogram-class-breaks` and `export-report` widgets extended instead of adding new widgets.
- S14 (legend reflects what is drawn) severity medium -> high.
- D02 (data freshness) now also covers offline sync and unsynced edits; its evidence is now `synth`.
- Plugin and marketplace version 0.2.0; README data table and install from `ignify-rd/gis-ui-ux-pro`.

## 0.1.0 - 2026-11-14

- Add `SKILL.md` (frontmatter `name` + `description`, workflows, query contract, worked example), plugin manifests (`.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`) and `README.md`.
- `claude plugin validate . --strict` passes. The marketplace manifest has a `metadata.description` to clear the strict-mode warning. The plugin-directory icon check (ICON_MISSING) is advisory and does not affect the result.
- Knowledge base: 250 rows in 9 files (rules 103, problems 22, palettes 33, widgets 22, layouts 9, stacks 61: mapbox-maplibre 20, deckgl 17, leaflet 13, openlayers 11). 46 tests pass.
- Evals (`evals/`): 3 scenarios, 20 trigger queries. With-skill 21/24 vs baseline 19/24 expected checks (single run per arm, n=1; indicative only). The skill adds rule ids, a symmetric-clamp InSAR legend and sourced/synth labels. Gaps found in the evals were fixed with 3 new synth rules: S18 (no-data legend class), D10 (source and date per layer), E09 (AIS match gate).
- Final-review fix wave: corrected rule counts (103) in SKILL.md/README with a packaging test, retyped `severity-5` and `detection-confidence` palettes as qualitative, `--persist -f json` keeps stdout valid JSON (status messages on stderr), accent-folding slugs with problem-id fallback, `--json` with `--blueprint`, match scores in the blueprint, `map` ignored as noise in problem search, clean error for a missing `--data-dir`, Leaflet lf-06 and OpenLayers ol-01 stack fixes, generic README install path.
