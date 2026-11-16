# gis-ui-ux-pro

A Claude Code skill for designing, building and reviewing the UI/UX of web maps, GIS dashboards and Earth-observation apps. It pairs a CSV knowledge base with a standard-library Python BM25 search script and a blueprint generator that turns a problem description ("flood mapping from Sentinel-1") into a dashboard design: layout, layers, palettes, widgets, temporal UI, interactions, alerts, pitfalls and a pre-delivery checklist.

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
python scripts/search.py "flood mapping" --blueprint --persist -o ../my-app -p "Flood Watch"
```

```
search.py QUERY [-d rule|problem|palette|widget|layout] [-s mapbox-maplibre|leaflet|openlayers|deckgl]
                [-n 1..20] [--json] [--full]
search.py "<problem description>" --blueprint [-f markdown|json] [--persist -o DIR -p NAME [--force]]
```

- Without `-d`, the domain is auto-detected (fallback `rule`).
- "No matches" exits 0 and suggests keywords. A `--blueprint` that matches no problem exits 1 and lists the problem ids.
- `--persist` writes `gis-design/<slug>/BLUEPRINT.md` and never overwrites without `--force`.
- If `python` is not found, use `python3` or `py -3`.

## Data

All files live in `skills/gis-ui-ux-pro/data/`. Rule-like rows carry `evidence`: `sourced` (copied from the cited `source_url`) or `synth` (synthesized guidance, not a single-source fact).

| File | Domain / flag | Rows |
|---|---|---|
| `rules.csv` | `-d rule` | 103 (accessibility 11, controls 11, symbology 18, layers 7, interaction 9, temporal 9, eo 9, widgets 10, layout 12, performance 7) |
| `problems.csv` | `-d problem`, `--blueprint` | 22 |
| `palettes.csv` | `-d palette` | 33 |
| `widgets.csv` | `-d widget` | 22 |
| `layouts.csv` | `-d layout` | 9 |
| `stacks/mapbox-maplibre.csv` | `-s mapbox-maplibre` | 20 |
| `stacks/leaflet.csv` | `-s leaflet` | 13 |
| `stacks/openlayers.csv` | `-s openlayers` | 11 |
| `stacks/deckgl.csv` | `-s deckgl` | 17 |

Problem ids: object-detection, maritime-awareness, land-change, surface-water-drought, flood, ground-deformation, wildfire, deforestation, oil-spill, crop-health, urban-planning, infrastructure-network, disaster-response, air-quality-heat, fleet-tracking, site-suitability, demographic-choropleth, real-estate, public-health, mining, coastal-erosion, crime-mapping.

`references/quick-reference.md` (all rules) and `references/checklist.md` (audit checklist) are generated from `rules.csv`.

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
