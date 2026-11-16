# gis-ui-ux-pro

A Claude Code skill for designing, building and reviewing the UI/UX of web maps, GIS dashboards and Earth-observation apps. It pairs a CSV knowledge base with a standard-library Python BM25 search script and a blueprint generator that turns a problem description ("flood mapping from Sentinel-1") into a dashboard design: layout, layers, palettes, widgets, temporal UI, interactions, alerts, pitfalls, a map signature (two visual directions plus a safe baseline) and a pre-delivery checklist.

It covers what generic UI skills don't: the map surface, cartography and color ramps, layers and legends, temporal comparison, EO specifics and map accessibility. Generic styling (fonts, brand colors, buttons) is left to `ui-ux-pro-max` / `impeccable`.

No dependencies beyond Python 3. Works on Windows (Git Bash, PowerShell) and POSIX.

## Install

### From a local path

```
/plugin marketplace add /path/to/gis-ui-ux-pro (Windows: `C:/path/to/gis-ui-ux-pro`)
/plugin install gis-ui-ux-pro@gis-ui-ux-pro
```

### From GitHub

```
/plugin marketplace add ignify-rd/gis-ui-ux-pro
/plugin install gis-ui-ux-pro@gis-ui-ux-pro
```

### Copy into a project

Copy `skills/gis-ui-ux-pro/` into any `.claude/skills/` directory (project or user level). Script paths in SKILL.md use `${CLAUDE_SKILL_DIR}`, so they work in both install modes.

## CLI usage

```bash
cd skills/gis-ui-ux-pro
python scripts/search.py "legend hidden layers" -d rule
python scripts/search.py "ndvi" -d palette -n 1 --full
python scripts/search.py "attribution control" -s leaflet
python scripts/search.py "vessel detection sentinel-1 ais" --blueprint
python scripts/search.py "citizen service requests by ward" --blueprint --intensity subtle
python scripts/search.py "tracking replay scrubber" -d direction -n 2
python scripts/search.py "flood mapping" --blueprint --persist -o ../my-app -p "Flood Watch"
```

```
search.py QUERY [-d rule|problem|palette|widget|layout|direction]
                [-s mapbox-maplibre|leaflet|openlayers|deckgl|cesium|ogc] [-n 1..20] [--json] [--full]
search.py "<problem description>" --blueprint [--intensity subtle|balanced|bold] [--direction ID]
                [-f markdown|json] [--persist -o DIR -p NAME [--force]]
```

- Without `-d`, the domain is auto-detected (fallback `rule`).
- "No matches" exits 0 and suggests keywords. A `--blueprint` that matches no problem exits 1 and lists the problem ids.
- `--intensity` and `--direction` work only with `--blueprint` (otherwise exit 2); an unknown direction id exits 2 and lists the ids.
- `--persist` writes `gis-design/<slug>/BLUEPRINT.md` and never overwrites without `--force`.
- If `python` is not found, use `python3` or `py -3`.

## Data

All files live in `skills/gis-ui-ux-pro/data/`. Rule-like rows carry `evidence`: `sourced` (copied from the cited `source_url`) or `synth` (synthesized guidance, not a single-source fact).

| File | Domain / flag | Rows |
|---|---|---|
| `rules.csv` | `-d rule` | 122 (accessibility 14, controls 11, symbology 20, layers 9, interaction 15, temporal 10, eo 10, widgets 12, layout 12, performance 9) |
| `problems.csv` | `-d problem`, `--blueprint` | 28 |
| `palettes.csv` | `-d palette` | 33 |
| `widgets.csv` | `-d widget` | 30 |
| `layouts.csv` | `-d layout` | 9 |
| `directions.csv` | `-d direction`, blueprint Signature | 12 |
| `stacks/mapbox-maplibre.csv` | `-s mapbox-maplibre` | 20 |
| `stacks/leaflet.csv` | `-s leaflet` | 13 |
| `stacks/openlayers.csv` | `-s openlayers` | 11 |
| `stacks/deckgl.csv` | `-s deckgl` | 17 |
| `stacks/cesium.csv` | `-s cesium` | 9 |
| `stacks/ogc.csv` | `-s ogc` (WMS/WFS/WMTS clients) | 8 |

Problem ids: object-detection, maritime-awareness, land-change, surface-water-drought, flood, ground-deformation, wildfire, deforestation, oil-spill, crop-health, urban-planning, infrastructure-network, disaster-response, air-quality-heat, fleet-tracking, site-suitability, demographic-choropleth, real-estate, public-health, mining, coastal-erosion, crime-mapping, service-requests, asset-survey, parcel-registry, enforcement-casework, data-catalog, vegetation-cover-admin.

Direction ids: civic-paper, field-atlas, night-ops, signal-track, orbital-lightbox, newsroom-story, canvas-studio, analytic-glow, living-atmosphere, conservation-signal, urban-twin, heritage-atlas.

`references/quick-reference.md` (all rules) and `references/checklist.md` (audit checklist) are generated from `rules.csv`.

## Map signature

Map products tend to look alike. The skill gives each one a distinct but familiar look on the map side, in three layers:

- **Locked conventions** - control positions, standard interactions and icons, CVD-safe data ramps from `palettes.csv`, attribution. Never varied.
- **Signature zones** - basemap recipe, panel surface, type pair (open-licensed fonts), one accent, motion, marker grammar and exactly one hero element.
- **Intensity** - `subtle` (public and civic), `balanced` (ops and analyst tools), `bold` (pre-sales, story, events). Each problem has a default; `--intensity` overrides it.

The blueprint's Signature section suggests two directions plus a safe `subtle` baseline, the locked conventions, a token table, the hero element with variations, and a short user-test plan. All suggested fonts are SIL Open Font License. The signature never recolours data or moves controls, and removing it leaves a fully usable app. In Claude, the skill runs a short discovery (at most 3 questions), presents the directions with text sketches, can produce an optional single-file MapLibre + OpenFreeMap mock (or hand the tokens to `impeccable`), and self-critiques before delivering.

## Contributing

After editing any CSV, run from the repo root:

```bash
python skills/gis-ui-ux-pro/scripts/validate_data.py
python skills/gis-ui-ux-pro/scripts/build_reference.py
python skills/gis-ui-ux-pro/scripts/build_reference.py --check
python -m unittest discover -s skills/gis-ui-ux-pro/scripts/tests -v
```

- Keep every row's `id` unique and its `keywords` in English.
- Mark a row `sourced` only when its content (including palette hex values) is copied from `source_url`; otherwise mark it `synth`.
- Keep `SKILL.md` under 300 lines; put detail in the data, not the skill body.

## Credits

Inspired by the `ui-ux-pro-max` skill (MIT): the CSV knowledge base plus BM25 search pattern and the query contract idea. The code here is written fresh. Data sources are cited per row in `source_url`; research notes are in `docs/research/`.

License: MIT (see `LICENSE`).
