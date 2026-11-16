"""Column schema, file map and enums for the gis-ui-ux-pro CSV knowledge base."""

COLUMNS = {
    "rule": ["id", "category", "name", "keywords", "do", "dont", "why", "severity",
             "evidence", "source_url", "checklist", "code_good", "code_bad"],
    "problem": ["id", "name", "keywords", "user_questions", "layers_default_on",
                "layers_default_off", "symbology", "widgets", "temporal", "interactions",
                "alerts", "pitfalls", "data_sources", "examples", "layout_id",
                "palette_ids", "rule_ids", "evidence", "source_url", "direction_ids",
                "intensity_default"],
    "direction": ["id", "name", "mood", "intensity_default", "intensity_range",
                  "fits_problems", "basemap_recipe", "reference_basemaps", "surface_recipe",
                  "type_pair", "accent_strategy", "motion_recipe", "marker_grammar",
                  "hero_element", "locked", "variation_axes", "pitfalls", "examples",
                  "keywords", "evidence", "source_url"],
    "palette": ["id", "name", "type", "use_for", "domain_range", "stops_hex",
                "dark_basemap_stops_hex", "classes", "cvd_safe", "keywords", "evidence",
                "source_url"],
    "widget": ["id", "name", "purpose", "use_when", "avoid_when", "required_states",
               "a11y", "rule_ids", "keywords", "slot"],
    "layout": ["id", "name", "use_when", "avoid_when", "regions", "ascii_sketch",
               "mobile_variant", "rule_ids", "keywords", "slots", "mobile_slots"],
    "stack": ["id", "category", "guideline", "keywords", "do", "dont", "code_good",
              "code_bad", "severity", "docs_url"],
}

FILES = {"rule": "rules.csv", "problem": "problems.csv", "palette": "palettes.csv",
         "widget": "widgets.csv", "layout": "layouts.csv",
         "direction": "directions.csv"}

STACKS = ("mapbox-maplibre", "leaflet", "openlayers", "deckgl", "cesium", "ogc")

SEARCH_FIELDS = {
    "rule": ["name", "keywords", "do", "dont", "why", "category"],
    "problem": ["name", "keywords", "user_questions", "layers_default_on", "symbology",
                "widgets", "pitfalls", "examples"],
    "palette": ["name", "keywords", "use_for", "type"],
    "widget": ["name", "keywords", "purpose", "use_when"],
    "layout": ["name", "keywords", "use_when", "regions"],
    "direction": ["name", "mood", "keywords", "fits_problems", "hero_element", "examples"],
    "stack": ["guideline", "keywords", "do", "dont", "category"],
}

ENUMS = {
    "severity": {"critical", "high", "medium", "low"},
    "evidence": {"sourced", "synth"},
    "palette_type": {"sequential", "diverging", "qualitative", "standard"},
    "category": {"layout", "controls", "layers", "symbology", "interaction", "temporal",
                 "widgets", "eo", "performance", "accessibility"},
    "intensity": {"subtle", "balanced", "bold"},
}

# Cells holding ';'-separated lists.
LIST_COLUMNS = {"rule_ids", "palette_ids", "stops_hex", "dark_basemap_stops_hex",
                "required_states", "direction_ids", "intensity_range", "fits_problems"}

INTENSITY_ORDER = ("subtle", "balanced", "bold")

# Screen regions a layout can declare (`slots`, `mobile_slots`) and a widget can ask for (`slot`).
# map-* corners exist implicitly whenever a layout has a `map` slot.
MAP_CORNERS = ("map-top-left", "map-top-right", "map-bottom-left", "map-bottom-right")
SLOTS = ("header", "action-bar", "kpi-strip", "filters", "panel", "list", "charts", "map",
         "drawer", "sheet", "timeline", "delta-strip", "ticker", "narrative", "status-bar",
         "footer") + MAP_CORNERS
