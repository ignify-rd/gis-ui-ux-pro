# gis-ui-ux-pro: GIS UI/UX design-intelligence skill — Design

Date: 2026-11-14. Status: approved by owner 2026-11-14.

## 1. Intent

The owner builds web GIS and remote-sensing products (React + mapbox-gl + Tailwind + Recharts). They want a skill that Claude uses when designing, building or reviewing the UI/UX of such apps. It should work like `ui-ux-pro-max` (local CSV knowledge base plus a stdlib Python search script), but cover what generic UI skills don't:

- the map surface itself
- cartography and color ramps
- layers and legends
- temporal comparison
- EO/remote-sensing specifics
- map accessibility
- above all: **for a given GIS problem type, what the screen should show**

The skill starts as a standalone git repo. Later it is installed as a Claude Code plugin from that repo, the same way the owner installs other skills.

## 2. Goals, non-goals, anti-goals

**Goals**
- G1. Given a problem description (for example "vessel detection from Sentinel-1 with AIS matching"), Claude can produce a dashboard blueprint: layout, layers (default on or off, symbology, palette), widgets, temporal UI, interactions, alert encoding and pitfalls.
- G2. Claude can look up GIS UI rules by topic: legend, time slider, attribution, cluster, swipe, NDVI ramp and so on. Each rule has do/don't, why, severity and a source.
- G3. Claude can audit an existing GIS screen against a GIS-specific pre-delivery checklist.
- G4. The skill installs as a Claude Code plugin from its repo, and also works when copied into a project's `.claude/skills/`.

**Non-goals**
- Generic UI styling: fonts, brand colors, buttons, general accessibility. That is left to `ui-ux-pro-max` / `impeccable`. SKILL.md says so and points there.
- A component library or npm package; backend, data processing or tiling pipelines.
- A multi-agent CLI installer (Cursor, Windsurf and so on). This may come later.

**Anti-goals** (failure even if it "works")
- Rules or palette hex values stated as fact without a source. Every row carries `source_url` and an `evidence` flag (`sourced` or `synth`).
- Becoming specific to one app. Content stays generic.
- A SKILL.md that bloats past about 300 lines, or a script that needs `pip install`.

## 3. Constraints
- Python 3 standard library only. The owner has Python 3.11 on Windows; scripts must work in Git Bash and in PowerShell.
- Skill format rules (from `docs/superpowers/research/2026-11-14-skill-authoring.md`):
  - `name` ≤ 64 characters, kebab-case, equal to the directory name
  - `description` ≤ 1024 characters, third person, with "Use when…" trigger terms
  - body under 500 lines
  - references one level deep
- Script paths in SKILL.md use `${CLAUDE_SKILL_DIR}`. Do not use `${CLAUDE_PLUGIN_ROOT}`: it breaks when the skill is copied to `.claude/skills/`, which is a bug found in the local ui-ux-pro-max copy.
- Content language: **everything in English** (SKILL.md, data, keywords, README, evals). Owner decision 2026-11-14.
- Tests must not depend on locating an upstream repo root. The ui-ux-pro-max copy has 4 test modules failing for that reason.

## 4. Approaches considered
| | Approach | Trade-off |
|---|---|---|
| A | Markdown only: SKILL.md + `references/*.md`, one playbook file per problem type | Cheapest and easy to edit by hand; gets harder to search as content grows |
| **B (chosen by owner)** | ui-ux-pro-max style: CSV knowledge base + BM25 search script + a "blueprint" generator | Most work and needs script maintenance; scales, can be queried precisely, and gives one consistent output per problem |
| C | Markdown + one problem CSV, script later | Middle path |

The owner picked B.

## 5. Design

### 5.1 Repo layout
Its own git repo, published at `ignify-rd/gis-ui-ux-pro`.

```
gis-ui-ux-pro/
├── .claude-plugin/
│   ├── plugin.json            # name, version 0.1.0, description, author, license MIT, keywords
│   └── marketplace.json       # name "gis-ui-ux-pro", owner, plugins:[{name:"gis-ui-ux-pro", source:"./"}]
├── skills/gis-ui-ux-pro/
│   ├── SKILL.md
│   ├── data/
│   │   ├── rules.csv
│   │   ├── problems.csv
│   │   ├── palettes.csv
│   │   ├── widgets.csv
│   │   ├── layouts.csv
│   │   └── stacks/{mapbox-maplibre,leaflet,openlayers,deckgl}.csv
│   ├── references/
│   │   ├── quick-reference.md # all rules, generated from rules.csv
│   │   └── checklist.md       # GIS pre-delivery / audit checklist
│   └── scripts/
│       ├── core.py            # BM25 + normalization + domain detection
│       ├── search.py          # CLI
│       ├── blueprint.py       # problem → dashboard blueprint
│       ├── build_reference.py # regenerates references/quick-reference.md
│       ├── validate_data.py   # data integrity
│       └── tests/             # unittest + relevance fixtures
├── evals/
│   ├── scenarios.md           # 3 task scenarios + expected behaviors
│   └── trigger-queries.json   # ~20 should/should-not-trigger prompts
├── docs/research/             # copies of the 3 research notes (provenance)
├── README.md                  # install + usage (English)
├── CHANGELOG.md
└── LICENSE                    # MIT
```

The `skills/` directory is the plugin default, so plugin.json needs no `skills` key.

Install, documented in README:
1. `/plugin marketplace add <path-or-owner/repo>`
2. `/plugin install gis-ui-ux-pro@gis-ui-ux-pro`

Alternative install: copy `skills/gis-ui-ux-pro/` into any `.claude/skills/`.

### 5.2 Data files (domains)
Every CSV has a stable `id` primary key, a `keywords` column (English search terms and synonyms, e.g. "landslide, slope failure, ground motion") and `source_url`. Rule-like rows also have `evidence` (`sourced` | `synth`).

| File / domain | Rows (target) | Columns | Seeded from |
|---|---|---|---|
| `rules.csv` (`rule`) | ~95 | id, category, name, keywords, do, dont, why, severity (critical/high/medium/low), evidence, source_url, code_good, code_bad (optional) | `research/…-gis-ui-rules.md`, categories L, C, Y, S, I, T, D, E, P, A |
| `problems.csv` (`problem`) | 22 | id, name, keywords, user_questions, layers_default_on, layers_default_off, symbology, widgets, temporal, interactions, alerts, pitfalls, data_sources, examples, layout_id, palette_ids, rule_ids, evidence, source_url | `research/…-gis-problem-playbooks.md`, sections 1–22 |
| `palettes.csv` (`palette`) | ~30 | id, name, type (sequential, diverging, qualitative, standard), use_for, domain_range, stops_hex, dark_basemap_stops_hex, classes, cvd_safe, keywords, evidence, source_url | See "Palettes" below |
| `widgets.csv` (`widget`) | ~25 | id, name, purpose, use_when, avoid_when, required_states (loading, empty, error, stale), a11y, rule_ids, keywords | See "Widgets" below |
| `layouts.csv` (`layout`) | ~10 | id, name, use_when, avoid_when, regions, ascii_sketch, mobile_variant, rule_ids, keywords | See "Layouts" below |
| `stacks/*.csv` (`--stack`) | 15–25 each | id, category, guideline, do, dont, code_good, code_bad, severity, docs_url | Needs fresh research from official docs |

**Palettes.** Hex values must be copied from the cited source, never invented. The list:
- ColorBrewer key ramps and CARTOColors
- viridis
- EPA AQI
- US Drought Monitor / CDI classes
- NDVI and NDWI
- InSAR velocity (diverging, centered on 0)
- dNBR burn severity
- fire age
- flood vs permanent water vs no-data hatch
- damage grading
- generic 5-level severity
- vessel types
- standard zoning colors
- ESA WorldCover legend
- detection confidence

**Widgets.** KPI tile, alert list, feature table, layer panel, legend, time slider, swipe compare, availability date picker, scene card, AOI draw/measure, confidence slider, review queue, time-series chart, histogram with class breaks, transition Sankey, detail drawer, filter chips, basemap switcher, geocoder, coordinate readout, freshness/status bar, export/report.

**Layouts.** Full-map + floating panels; shell + action bar; ops dashboard (KPIs top, map center, list right); split map/dashboard; list-first locator; compare split view; mobile bottom sheet; wall display; scrolly story.

**Problem ids** (from research): object-detection, maritime-awareness, land-change, surface-water-drought, flood, ground-deformation, wildfire, deforestation, oil-spill, crop-health, urban-planning, infrastructure-network, disaster-response, air-quality-heat, fleet-tracking, site-suitability, demographic-choropleth, real-estate, public-health, mining, coastal-erosion, crime-mapping.

Cross-references (`rule_ids`, `palette_ids`, `layout_id`) must point at existing ids. `validate_data.py` enforces this.

### 5.3 Scripts
- **`core.py`**
  - BM25 over the chosen CSV; text normalization (lowercase, accent-folding, stopwords).
  - A GIS synonym map, for example:
    - `insar → ground deformation`
    - `sar → radar`
    - `ais → vessel`
    - `ndvi → vegetation`
    - `choropleth → thematic`
  - Domain auto-detection by keyword phrases, with fallback `rule`, and a minimum score floor so junk doesn't come back as a match.
- **`search.py`** CLI:
  ```
  search.py "<query>" [-d rule|problem|palette|widget|layout] [-s mapbox-maplibre|leaflet|openlayers|deckgl]
            [-n 1..20 (default 3)] [--json] [--full]
  search.py "<problem description>" --blueprint [-f markdown|json] [--persist -o <dir>] [-p <project name>]
  ```
  - Default output is markdown: `### Result N` blocks with `- **col:** value`.
  - Zero hits prints "No matches" plus the closest known keywords.
- **`blueprint.py`** (via `--blueprint`), the G1 deliverable:
  1. Match the description to one `problems.csv` row; also show the runner-up so Claude can sanity-check.
  2. Expand it: the referenced layout (with its ASCII sketch), the layers table (on/off plus symbology plus resolved palette hex), widgets resolved against `widgets.csv` (with required states), temporal UI, interactions, alert encoding, pitfalls, and the critical/high rules from `rule_ids`.
  3. End with the checklist items relevant to that problem.

  `--persist` writes `gis-design/<slug>/BLUEPRINT.md` in the target project.
- **`build_reference.py`** regenerates `references/quick-reference.md` from `rules.csv`, so the two never drift.
- **`validate_data.py`** checks:
  - headers
  - unique ids
  - cross-reference integrity
  - hex format
  - severity/evidence enums
  - non-empty `source_url` for `sourced` rows

  It exits non-zero on failure with specific messages.

### 5.4 SKILL.md (target ≤ 300 lines)
Frontmatter:
- `name: gis-ui-ux-pro`
- `description` (third person) along the lines of: "GIS and remote-sensing UI/UX intelligence: map layouts, layer panels, legends, color ramps, time sliders and before/after compare, EO imagery display, map accessibility, and per-problem dashboard blueprints (vessel detection, flood, landslide/InSAR, deforestation, water change, wildfire, …). Use when designing, building or reviewing web maps, GIS dashboards, WebGIS or Earth-observation apps (mapbox-gl, MapLibre, Leaflet, OpenLayers, deck.gl)."

Body sections:
1. When to apply / when to hand off to ui-ux-pro-max.
2. Rule category priority table:
   1. Accessibility & legibility
   2. Map chrome & attribution
   3. Symbology & legend
   4. Layers
   5. Interaction
   6. Temporal
   7. EO specifics
   8. Widgets
   9. Layout
   10. Performance
3. How to run the script, with `${CLAUDE_SKILL_DIR}` paths and the Python fallback order `python` → `python3` → `py -3`.
4. Workflow for a new screen or app:
   - identify the problem → `--blueprint`
   - layout
   - targeted domain searches
   - `--stack`
   - run `references/checklist.md` before delivering
5. Workflow for reviewing an existing screen: read the code or screenshot, run the checklist, look up each failing item with `-d rule`, and report findings with rule ids.
6. A query contract (one intent, 2–5 terms, retry once, label fallbacks), adapted from ui-ux-pro-max.
7. A short worked example.

### 5.5 Testing and evals
- `python -m unittest discover -s skills/gis-ui-ux-pro/scripts/tests`. It covers:
  - BM25 sanity
  - domain detection
  - about 30 relevance fixtures (query → expected top id, e.g. "landslide insar" → ground-deformation, "dark vessels without AIS" → maritime-awareness)
  - a blueprint smoke test for every problem id
  - `validate_data.py` passing
- `evals/scenarios.md` has three scenarios. Each is run once with and once without the skill, and the differences are noted in the README or CHANGELOG.
  1. Design a dashboard for detecting vessels with Sentinel-1 + AIS. Expected:
     - dark detections visually distinct
     - confidence slider
     - scene date shown
     - "dark ≠ illegal" pitfall
  2. Review an existing water-area-change screen (a private app screen as test bed). Expected:
     - flags freshness
     - flags the no-data class
     - flags fixed index ranges
     - flags legend issues
  3. Choose symbology for an InSAR landslide app. Expected:
     - diverging ramp centered on 0 with a symmetric clamp
     - per-point time series
     - line-of-sight (LOS) explanation
- `evals/trigger-queries.json` holds about 10 should-trigger and about 10 near-miss prompts, the near misses being generic dashboard and non-map UI. It is used to tune the description by hand.
- `claude plugin validate . --strict` passes, if the CLI is available.

## 6. Decided by owner
- Approach B (CSV + search script), modeled on ui-ux-pro-max.
- The skill's user is the owner, building GIS web UI/UX (map-centric web apps).
- It is a standalone repo first, installed later as a plugin.

## 7. Claude's calls (owner can override)
- Name `gis-ui-ux-pro`. Repo location `GIS_ws/gis-ui-ux-pro/`. MIT license. All content in English (owner decision).
- Generic UI is deferred to ui-ux-pro-max / impeccable, not duplicated.
- Stacks: mapbox-maplibre, leaflet, openlayers, deckgl.
- Code is written fresh, not copied from ui-ux-pro-max. If any snippet is adapted, keep the MIT attribution in LICENSE/README.
- `${CLAUDE_SKILL_DIR}` instead of `${CLAUDE_PLUGIN_ROOT}` for script paths.

## 7b. Calls made after the builder review (owner can override)
- **Palettes and rules with no authoritative source.** Keep them, but mark them `evidence=synth`. Give them hex values chosen by Claude that pass CVD-safety and contrast checks. In `source_url`, put the closest supporting source, or leave it empty. This covers fire age, damage grading, generic severity, vessel types, detection confidence, flood/no-data, and every `dark_basemap_stops_hex`. `validate_data.py` requires `source_url` only for `sourced` rows. The anti-goal in §2 is therefore narrowed: unsourced content is allowed when it is labeled `synth`. It must never pass as sourced.
- **Research is in scope.** The plan starts with a sourcing phase that covers:
  - the 4 stack CSVs, from official docs
  - sourced palette hex values (ColorBrewer, CARTO, EPA AQI, USDM, ESA WorldCover, viridis)
  - re-checking the *(nv)* URLs and the items listed as unverified in the research notes

  Anything that can't be verified is downgraded to `synth`. The three unread follow-up sources (OCHA stylebook, Roth 2012, ICA heuristics) are optional.
- **Checklist comes from data.** `rules.csv` gets a `checklist` column (yes/no) holding the short check question. `build_reference.py` generates both `references/quick-reference.md` and `references/checklist.md`. For a blueprint, the relevant checklist is the checklist rules in that problem's `rule_ids`, plus all `critical` checklist rules.
- **Evals.** A subagent runs them with the skill, and another runs them without it, at the end of the build. They are required before the work is called done, but they report findings rather than gate a pass/fail. Before scenario 2 is used, check the current test-bed screen. If it no longer has the expected issues, rewrite the scenario's expectations.
- **Overlap with platform-API skills.** Skills that operate a GIS/EO platform's API are out of scope; this one designs UI. `trigger-queries.json` includes near-misses such as "create a vessel-watch project via a GIS platform's API" (should NOT trigger).
- **Delivery order.** Everything in this spec ships as v0.1.0, built in this order:
  1. scripts and validator
  2. rules and problems
  3. palettes, widgets and layouts
  4. stacks
  5. references, SKILL.md, plugin files, evals

- **Author/owner metadata:** `Khanhle19` in `plugin.json`, `marketplace.json` and `LICENSE`. The README documents a local-path install and `ignify-rd/gis-ui-ux-pro` for GitHub.

## 8. Left to the builder
- BM25 parameters, score floors, synonym list and stopwords.
- Exact row wording and splitting or merging rules, as long as every research rule lands in some row.
- How many stack rows to write, based on official docs (mapbox-gl/MapLibre style spec and controls, Leaflet accessibility, OpenLayers controls, deck.gl picking and performance).
- Blueprint output formatting details.

## 9. Sources
- `docs/superpowers/research/2026-11-14-skill-authoring.md`
- `docs/superpowers/research/2026-11-14-gis-ui-rules.md`
- `docs/superpowers/research/2026-11-14-gis-problem-playbooks.md`
