"""Column schema, file map and enums for the gis-ui-ux-pro CSV knowledge base."""

COLUMNS = {
    "rule": ["id", "category", "name", "keywords", "do", "dont", "why", "severity",
             "evidence", "source_url", "checklist", "code_good", "code_bad"],
    "problem": ["id", "name", "keywords", "user_questions", "layers_default_on",
                "layers_default_off", "symbology", "widgets", "temporal", "interactions",
                "alerts", "pitfalls", "data_sources", "examples", "layout_id",
                "palette_ids", "rule_ids", "evidence", "source_url"],
    "palette": ["id", "name", "type", "use_for", "domain_range", "stops_hex",
                "dark_basemap_stops_hex", "classes", "cvd_safe", "keywords", "evidence",
                "source_url"],
    "widget": ["id", "name", "purpose", "use_when", "avoid_when", "required_states",
               "a11y", "rule_ids", "keywords"],
    "layout": ["id", "name", "use_when", "avoid_when", "regions", "ascii_sketch",
               "mobile_variant", "rule_ids", "keywords"],
    "stack": ["id", "category", "guideline", "keywords", "do", "dont", "code_good",
              "code_bad", "severity", "docs_url"],
}

FILES = {"rule": "rules.csv", "problem": "problems.csv", "palette": "palettes.csv",
         "widget": "widgets.csv", "layout": "layouts.csv"}

STACKS = ("mapbox-maplibre", "leaflet", "openlayers", "deckgl")

SEARCH_FIELDS = {
    "rule": ["name", "keywords", "do", "dont", "why", "category"],
    "problem": ["name", "keywords", "user_questions", "layers_default_on", "symbology",
                "widgets", "pitfalls", "examples"],
    "palette": ["name", "keywords", "use_for", "type"],
    "widget": ["name", "keywords", "purpose", "use_when"],
    "layout": ["name", "keywords", "use_when", "regions"],
    "stack": ["guideline", "keywords", "do", "dont", "category"],
}

ENUMS = {
    "severity": {"critical", "high", "medium", "low"},
    "evidence": {"sourced", "synth"},
    "palette_type": {"sequential", "diverging", "qualitative", "standard"},
    "category": {"layout", "controls", "layers", "symbology", "interaction", "temporal",
                 "widgets", "eo", "performance", "accessibility"},
}

# Cells holding ';'-separated lists.
LIST_COLUMNS = {"rule_ids", "palette_ids", "stops_hex", "dark_basemap_stops_hex",
                "required_states"}
