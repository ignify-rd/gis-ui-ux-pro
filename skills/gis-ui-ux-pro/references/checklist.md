# GIS UI/UX Audit Checklist

Generated from `data/rules.csv`. Tick each item while auditing a screen; critical items come first in each group.

## Accessibility

- [ ] Is there a text summary and feature table/list for the map content? (A01, critical)
- [ ] Can the map and features be operated with the keyboard alone? (A02, critical)
- [ ] Can keyboard users tab out of the map, with a skip link before it? (A03, critical)
- [ ] Is every color-coded meaning also shown by icon, pattern or label? (A07, critical)
- [ ] Is focus visible and the tab order logical? (A04, high)
- [ ] Do pan, swipe and the time slider each have a non-drag alternative? (A05, high)
- [ ] Do text (4.5:1) and symbols or outlines (3:1) meet contrast minimums? (A06, high)
- [ ] Do markers have accessible names, and are decorative maps inert? (A08, high)
- [ ] Does a popup take focus when it opens and return it on close? (A10, high)
- [ ] Does the camera jump instead of fly, and do animations stop, under prefers-reduced-motion? (A13, high)
- [ ] Are numbers, dates and area units locale-formatted and every control label translated, with RTL handled? (A12, medium)
- [ ] Are panels over the map solid, or is blur limited to calm areas with a reduce-transparency option? (A14, medium)

## Controls

- [ ] Is attribution visible on load without any interaction, and findable after it collapses? (C01, critical)
- [ ] Are both the Mapbox logo and attribution text visible and unmodified? (C02, critical)
- [ ] When using Leaflet or OpenLayers, is the tile provider attribution added explicitly? (C03, critical)
- [ ] Can users reach any location by search or coordinate entry, without dragging the map? (C09, high)
- [ ] Do controls follow corner conventions (nav top-right, scale bottom-left, attribution bottom)? (C04, medium)

## Symbology

- [ ] Does every choropleth show a normalized rate rather than raw counts? (S01, critical)
- [ ] Is the palette colorblind-safe, with no red-green-only encoding? (S09, critical)
- [ ] Are absolute totals shown with proportional symbols or dots rather than fills? (S02, high)
- [ ] Is a dot density map drawn in an equal-area projection? (S03, high)
- [ ] Is the number of classes within the limit for the ramp type? (S04, high)
- [ ] Was the classification method chosen deliberately (fixed breaks when maps are compared)? (S05, high)
- [ ] Does the ramp type (sequential, diverging, qualitative) match the data? (S06, high)
- [ ] Does the ramp lightness direction match the basemap (dark=high on light, bright=high on dark)? (S07, high)
- [ ] Are continuous fields free of rainbow or jet ramps? (S08, high)
- [ ] Is the basemap muted enough for the data layer to dominate? (S10, high)
- [ ] Does the legend list only visible, in-scale layers and follow the active filter? (S14, high)
- [ ] Are dense point layers clustered at low zoom, with clusterMaxZoom set? (S16, high)
- [ ] Does the legend have a class for no data that is separate from normal and from zero? (S18, high)
- [ ] Does the visual signature leave data ramps and control positions untouched? (S19, medium)
- [ ] Do labels on the dark basemap stay readable, with halos matched to the land colour? (S20, medium)

## Layers

- [ ] Are non-essential layers off by default? (Y01, high)
- [ ] Does every layer have a min/max visible zoom range? (Y02, high)
- [ ] Are layer titles and field names human-readable, with IDs and codes hidden? (Y04, high)
- [ ] Are rasters under vectors and reference labels on top? (Y05, high)
- [ ] Does import check required shapefile parts, warn on missing .prj/.cpg, and preview the count? (Y08, high)
- [ ] Are WMS legends fetched with SCALE and only queryable layers sent to GetFeatureInfo? (Y09, medium)

## Interaction

- [ ] Does hover only highlight (feature-state, cursor) while click opens the details? (I02, high)
- [ ] Do popups show a curated, formatted set of fields with the title first? (I04, high)
- [ ] Do map, chart and table share one selection state and highlight color? (I05, high)
- [ ] Are active filters shown as chips with an 'N of M features' count? (I09, high)
- [ ] Are popup and identify values inserted as text (setText or DOM), never as raw HTML from data? (I10, high)
- [ ] Are personal fields excluded from the query and export for roles that do not need them? (I11, high)
- [ ] Do AI map actions show a preview, confirm destructive changes, and offer one-step undo? (I12, high)
- [ ] Does the query builder use plain-word predicates and show a count before apply? (I13, medium)
- [ ] Does changing a parent unit clear child selections, zoom to the unit, and update the breadcrumb? (I14, medium)
- [ ] Is a visible search box kept even when a command bar exists? (I16, medium)

## Temporal

- [ ] Is there a swipe, fade or lens compare mode for before and after imagery? (T01, high)
- [ ] Are the dates labeled on both sides of the compare view? (T02, high)
- [ ] Is there an adjustable cloud cover filter, defaulting to about 30%? (T06, high)
- [ ] Does the UI say cloud % is per scene (or compute it per AOI)? (T07, high)
- [ ] Are cloudy observations flagged or removed from time series? (T09, high)
- [ ] Are times stored and queried in UTC, shown with a zone label, and are date-range bounds converted to UTC? (T10, high)

## EO

- [ ] Are composites named by purpose instead of bare band codes? (E01, high)
- [ ] Do index layers use a fixed domain with a ticked legend? (E03, high)
- [ ] Do scene cards show thumbnail, date, AOI coverage, resolution, sensor and cloud %? (E05, high)
- [ ] Is detection confidence shown, filterable by threshold, and visually encoded? (E08, high)
- [ ] Does the UI state the AIS match radius and time tolerance, and the offset to the SAR time? (E09, high)
- [ ] Does pixel identify show a unit or scale factor with the value? (E10, medium)

## Widgets

- [ ] Does every KPI have units and a reference value? (D01, high)
- [ ] Is a last-updated time shown and refresh aligned with the layer? (D02, high)
- [ ] Are statistics pre-aggregated and only needed fields loaded? (D03, high)
- [ ] Do map and charts share one categorical palette? (D06, high)
- [ ] Is uncertainty encoded (VSUP or a confidence channel)? (D08, high)
- [ ] Does the alert list sort by severity/time and sync with map selection both ways? (D09, high)
- [ ] Does every export include title, legend, scale, source/date, active filter or extent, and text attribution? (D11, high)
- [ ] Does every layer show its source and acquisition date without hover? (D10, medium)
- [ ] Are only valid transitions offered, with who/when/from-to/remark recorded? (D12, medium)

## Layout

- [ ] Was the layout (full map vs map plus panel) chosen from the main user task? (L01, high)
- [ ] Do tools live in a header plus action bar with collapsible panels instead of always-open widgets on the map? (L03, high)
- [ ] Is the most important element (map or headline KPI) visibly the largest? (L05, high)
- [ ] Are related elements (legend and map, list and details) placed together? (L06, high)
- [ ] Was the layout tested on the real target display for the intended audience? (L07, high)
- [ ] Does every element on the page answer a user question (no nice-to-have clutter)? (L08, high)
- [ ] Below 768px is the map on top with a bottom sheet instead of a side panel? (L09, high)
- [ ] Does the stacking order follow basemap, thematic, reference, highlight, controls, panels, popups, modals, with attribution uncovered? (L11, high)

## Performance

- [ ] Are large datasets served as vector tiles instead of one big GeoJSON? (P01, high)
- [ ] Is GeoJSON trimmed (6 decimals, needed properties only, loaded by URL, maxzoom set)? (P02, high)
- [ ] Are points above a few hundred rendered as layers (clustered), not DOM markers? (P03, high)
- [ ] Does each layer show its own error state with retry, leaving others working? (P06, high)
- [ ] Is the map captured on idle/rendercomplete without preserveDrawingBuffer and without moving the live view? (P08, medium)
- [ ] Are tile URLs stable, changing only when the data version changes? (P09, medium)
