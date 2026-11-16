# Design brief: Sentinel-1 vessel detection and AIS cross-check dashboard

Users: maritime analysts watching a port and its approaches.
Basis: gis-ui-ux-pro blueprints `maritime-awareness` (primary) and `object-detection` (runner-up, used for review queue and confidence). Rule ids in brackets. Items marked (synth) are recommended defaults, not sourced guidance, and the team may override them. Hex values come from the skill's palettes, which are all synth.

Core question the screen answers: which SAR detections have no AIS partner (candidate dark vessels), which AIS vessels did SAR not see, and how sure are we.

## 1. Layout

Map-first ops dashboard (KPIs top, filters left, map center, work queue right, timeline bottom). It is not data-first, because analysts spend most of their time on the map.

```
+----------------------------------------------------------------------+
| KPI: SAR dets | Matched | Unmatched | AIS w/o SAR | Scene age | FRESH  |
+--------+------------------------------------------+------------------+
| Filter | [search MMSI/IMO/name/coords]      [AOI] |  Review queue    |
| chips  |                                          |  (unmatched,     |
| Layers |                  MAP                     |   sorted by      |
| Legend |   scene footprint, detections, AIS       |   conf x zone)   |
|        |                         [scale][attrib]  |  --- detail      |
|        |                                          |  drawer on click |
+--------+------------------------------------------+------------------+
| Timeline: scene passes (ticks) | AIS replay window | counts per pass  |
+----------------------------------------------------------------------+
```

- Left rail (about 260 px, collapsible): active-filter chips with "N of M shown" and clear-all [I09], layer panel grouped by theme [Y], and the legend. The legend lives with the layer panel and lists only visible layers.
- Right panel (about 360 px): review queue by default. Selecting an item swaps in a detail drawer with a back button. Items are sorted by severity then time. Click zooms and highlights, and selecting on the map scrolls the list to the item [D09, I05]. One shared selection state and one highlight color across map, table and chart.
- Top strip: 4 to 5 KPIs, each with units and a reference value such as the previous pass or a 30-day median [D01]. A freshness bar shows the latest S1 acquisition time and the latest AIS message time as two separate clocks [D02].
- Bottom timeline: S1 passes appear as ticks. Selecting a pass sets the scene, and the AIS window then auto-centers on the acquisition time.
- Mobile or narrow: KPIs scroll horizontally, the map takes about 50 percent of the height, and the queue and drawer sit in a bottom sheet.
- Text alternative: a feature table of all detections with match status (list view toggle) provides the non-map view [A01]. The map is keyboard operable, with a skip link before it [A02, A03].
- Dark theme default for a watch-floor environment. Neutral dark basemap with muted land and bathymetry so that markers carry the color.

## 2. Map layers and symbology

Draw order, bottom to top. Everything is z-ordered so selection and alerts stay on top.

| # | Layer | Default | Symbology |
|---|---|---|---|
| 1 | Basemap: dark nautical or neutral, with port and land context | on | Low saturation. Attribution visible on load [C01, C03]. |
| 2 | Optional S1 backscatter image (VV or VH, in dB, fixed stretch) | off, appears at zoom 11 and above | Grayscale. Fixed dB range, with the legend note "water dark, ships bright" [E04]. |
| 3 | Zones: port geofence, anchorage, fairway or TSS, MPA, restricted areas | on, outlines only | Thin dashed outlines, labeled. Fills only on hover. |
| 4 | S1 scene footprint with date and orbit pass | on | Hairline outline plus a date label. Shows coverage and swath edge. |
| 5 | Land and coastal exclusion mask | on | Hatched gray. Marks the area where detection is suppressed, so empty does not read as "no ships". |
| 6 | Low-confidence detections | on, or off by a threshold | Hollow small ring, opacity driven by confidence [E08]. |
| 7 | SAR detections matched to AIS | on | Filled marker with a thin link line to its AIS position. Color is the vessel type from AIS. |
| 8 | SAR detections not matched (candidate dark) | on | Magenta #D81D74, diamond shape, bold outline. Always above all other point layers. Different shape from AIS markers. |
| 9 | AIS vessels at scene time | on | Arrow rotated to heading, with COG fallback. Color by type: #148EBF, #B74C1B, #148045, #8148DA, #B5810A, #8C8C8C (unknown). |
| 10 | AIS vessels expected inside the scene but not detected | on | Dashed hollow arrow with a "?" glyph. Often a small vessel, a sea-state effect or a radar shadow, so not an alert by itself. |
| 11 | Match search ellipse (selected only) | on selection | Dotted ellipse around the SAR position showing the time-propagated AIS uncertainty. |
| 12 | Selected vessel track and AIS gap markers (start, end) | on selection | Thin line with time ticks. Gap is a dashed segment with two end glyphs. |
| 13 | Density heatmap (historical traffic) | off | Single-hue sequential. It is shown only for context. |
| 14 | Image chip overlay | on selection | Small SAR chip in the drawer, with a link to a ruler tool. |

Symbology rules:
- Shape carries match status, and color carries type or severity. Never color alone [A07]. Shapes: arrow means AIS, circle means matched SAR, diamond means unmatched SAR, dashed arrow means AIS not seen in SAR.
- Confidence maps to opacity and outline weight, not hue. A threshold slider filters it and defaults to a team-agreed value. Detection hue is separate from the confidence ramp (blue to violet to magenta #2086CF, #6152E7, #D81D74), which is used only in the drawer or table [E08, D08].
- Palette must stay colorblind safe. Magenta against the blues, greens and browns is distinct, and the shape differences are the backup [S09].
- Size encodes vessel length estimate in 3 steps, with a minimum visible size. At low zoom, cluster detections with a count bubble and a split by matched or unmatched, with a set clusterMaxZoom [S16]. The cluster color shows unmatched if any child is unmatched.
- Scale-range rules: clusters below about zoom 9, individual markers above it, labels (name or MMSI) above about zoom 13.
- Large AIS history is served as vector tiles, and only the selected vessel's track is drawn as a line [P01]. Never render global tracks.

## 3. Controls

- Search box: MMSI, IMO, name, or lat/lon coordinates. Results fly to the target [C].
- Scene picker: timeline ticks plus a scene card (acquisition datetime in UTC, mode and polarization, orbit direction, pass, coverage percent of the AOI) [E05, T06]. It opens on the latest scene covering the AOI.
- Compare: swipe between two passes of the same AOI, with a date label on each half [T01, T02]. Also a "new since previous pass" filter chip.
- AIS time window: default is scene time with a tolerance of plus or minus a set number of minutes, shown on the control. Analyst can widen it. Replay (play, step) for the selected vessel.
- Filters (chips with counts): match status, vessel type, flag, length class, confidence minimum, zone (inside or outside), AIS state (active, gap, never seen). Always show "N of M shown" and a clear-all button [I09].
- Match parameters (advanced, collapsed): max distance, time tolerance, heading consistency. Changing them re-labels matches and shows a before and after count.
- AOI tools: draw a polygon, save a geofence, or pick a port zone. Alerts attach to the geofence.
- Layer panel: grouped (Detections, AIS, Zones, Imagery, Context), with opacity sliders for imagery and heatmap, and a greyed label with a "zoom in" hint when a layer is out of its scale range [Y].
- Review actions in queue and drawer: confirm, reject (false positive such as wind farm, platform, ice, wave or ambiguity), and label (likely fishing, non-fishing, unknown). Keyboard shortcuts for next, confirm, reject.
- Standard map chrome: zoom, scale bar, north arrow, coordinate readout with a copy button, basemap switcher, fullscreen. Attribution always visible [C01]. URL stores view, scene, filters and selection so a view can be shared.
- Export: the current queue as CSV or GeoJSON, plus a snapshot (map and metadata) report for a briefing.

## 4. Legend

A persistent collapsible legend that shows only the visible layers and also reflects the current filters.
1. Match status (shape key): arrow = AIS vessel; filled circle = SAR matched to AIS; magenta diamond = SAR with no AIS match; dashed "?" arrow = AIS expected but not detected; dotted ellipse = search area.
2. Vessel type color swatches, with a gray "unknown" entry.
3. Confidence key: a three-step opacity and outline sample with the current threshold marked.
4. Size key: three length classes.
5. Zones: line styles for port, anchorage, MPA, restricted.
6. Footprints and masks: scene footprint, hatched land or exclusion mask, "no coverage".
7. Imagery note (when SAR is on): dB range, polarization, "bright = strong return (metal, ships, waves), dark = calm water".
8. Data clocks: S1 acquisition time and AIS source and age.

## 5. Widgets and states

Each widget has loading, empty, error and stale states [D].
- KPI tiles: SAR detections, matched, unmatched (candidate dark), AIS not detected, with a delta against the previous pass. Empty means "0 detections in scene", and it must be distinguishable from "no coverage".
- Review queue and alert list: rows show a mini symbol, location, confidence, length, zone, and time. Severity encodes with icon plus text.
- Detail drawer: SAR chip, attributes (length, heading estimate, confidence, scene id), nearest AIS candidates with the match score and why the pair was rejected or accepted, vessel profile if AIS exists, and a track timeline with gaps.
- Feature table: sortable and exportable, and doubles as the accessible equivalent of the map [A01].
- Freshness bar: S1 scene age, AIS latest message age, and AIS source type (terrestrial or satellite). It turns amber and says "stale" past a set limit [D02].
- Trend chart: detections per pass with matched and unmatched stacked, clickable to select a scene.

## 6. Interaction

- Hover shows a short tooltip (type, MMSI or "no AIS", confidence). Click opens the full drawer and the track, so hover is never the only path [I].
- Selecting a SAR detection draws its candidate AIS partners with lines and scores. Selecting an AIS arrow shows its SAR counterpart or "not detected".
- Alerts are triggered by: unmatched detection inside a port geofence or a restricted zone, unmatched near a fairway, an AIS gap that overlaps the scene, an AIS position far from the SAR position, and a size mismatch. Severity is a numeric score plus a label, and a "why flagged" line.
- Use plain wording: "unmatched detection" or "candidate dark vessel", not "illegal" or "suspect".

## 7. Pitfalls to avoid

1. Treating "no AIS match" as "dark ship" or as illegal. Gaps can be technical, the AIS may be out of range, and small craft may not carry AIS. Say "unmatched" and provide the reasons list.
2. Not separating AIS from SAR visually (the blueprint pitfall). Use distinct shapes and a distinct unmatched color.
3. Ignoring the time offset. AIS and the S1 pass are never simultaneous, so a vessel moves between them. Dead-reckon or draw the search ellipse, and show the offset in minutes.
4. Hiding AIS reception gaps. Show terrestrial and satellite coverage, or at least a "low AIS coverage" shading, so a missing AIS is not misread.
5. Showing model output as certain. Show confidence and a threshold slider, and keep the review queue [E08, D08].
6. Empty map read as "no ships". Show swath edges, land mask, the nodata area, and scenes not covering the AOI.
7. SAR artefacts mislabeled as vessels: ambiguities (azimuth ghosts), wind-farm turbines, offshore platforms, buoys, breakwaters, rough sea and ice. Offer reject reasons and a known-fixed-objects layer.
8. Port clutter: dense quays and moored ships merge in SAR. Show a lower reliability message inside the harbor mask and not a crisp count.
9. Wrong size or heading claims. SAR length and heading are estimates, so label them "est." and show an error range.
10. Raw linear backscatter or a changing stretch between scenes. Keep dB with a fixed range and a legend note [E04].
11. Color-only meaning, or red-green coding. Use shape plus color and a CVD-safe palette [A07, S09].
12. Rendering tracks for everything, or thousands of markers unclustered. Track only the selection, cluster at low zoom, tile the data [S16, P01].
13. Timezone confusion. Show UTC everywhere, with local time on request.
14. Hiding freshness, or hiding the AIS source and age. Always show two clocks [D02].
15. Basemap too busy or too bright, which drowns the magenta markers. Keep the base muted.
16. Attribution or the basemap provider's logo hidden by panels [C01, C03]. Keep the right panel from covering the map's corner controls.
17. Alert overload: no deduplication, no ack state. Group repeated detections of one anchored vessel across passes and keep an acknowledged state.
18. Sensitive-data handling: commercial AIS licensing and watermarks on exports. Put the data source in each export.

## 8. Pre-delivery checklist

- [ ] Dense detections cluster at low zoom with clusterMaxZoom set (S16)
- [ ] AIS history served as vector tiles and no global tracks (P01)
- [ ] Every KPI has units and a reference value (D01)
- [ ] Freshness shown for both S1 and AIS (D02)
- [ ] Alert list sorted by severity and time, synced both ways with the map (D09)
- [ ] One shared selection state across map, table and drawer (I05)
- [ ] Active filters as chips with "N of M" and clear-all (I09)
- [ ] Every color meaning also has a shape, icon or label (A07)
- [ ] CVD-safe palette (S09)
- [ ] Attribution visible on load (C01, C03)
- [ ] Text summary and feature table equivalent of the map (A01)
- [ ] Keyboard operation and skip link around the map (A02, A03)
- [ ] SAR displayed in dB with a fixed range and note (E04)
- [ ] Detection confidence shown, filterable and visually encoded (E08)
- [ ] Compare mode with dates on both halves (T01, T02)

Evidence note: the blueprint, palettes and the pitfall list come from `synth` entries in the knowledge base, so treat them as recommended defaults. The accessibility, attribution and SAR in dB rules are from cited sources. Pitfalls 3 and 7 to 9, 17 and 18 and the match-ellipse design are general domain advice, not from the knowledge base.
