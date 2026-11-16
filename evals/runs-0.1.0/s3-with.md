# InSAR slow-landslide viewer: symbology and interaction design

Basis: gis-ui-ux-pro blueprint `ground-deformation` (runner-up infrastructure-network, which fits the road-corridor angle). Rule ids are cited. Items marked (synth) are recommended defaults, not authoritative sources. You can override them.

## 1. Layout
Split map and dashboard. The map is on the left. On the right are a detail drawer, a time-series chart, a velocity histogram and a ranked table of road segments. Filters are along the top.
On mobile the map takes about 50% of the height, with tabs below and a bottom sheet for details.
Use one shared selection state and one highlight colour across map, chart and table (I05).

## 2. Velocity points (Sentinel-1 PS)

**Ramp.** Use a diverging ramp centred on 0 with a symmetric clamp (S06, S08, S09). No rainbow or jet. Avoid green, so the ramp stays safe for red-green colour blindness.
- Palette `insar-velocity` (synth, 7 classes, checked for colour-blind safety by the knowledge base):
  - Light basemap: `#B2182B #EF6548 #FDD49E #F4F1E6 #A6D8EA #4A90C8 #1F4E9E`
  - Dark basemap: `#F26B5E #D98B5F #8C6A55 #454545 #4F7F96 #5AA7D6 #7DB8F2`
- Sourced alternative: ColorBrewer RdBu-7 (`#b2182b #ef8a62 #fddbc7 #f7f7f7 #d1e5f0 #67a9cf #2166ac`). Its colour-blind safety is unverified.

**Direction convention.** Warm colours mean motion away from the satellite (negative LOS velocity, for example downslope or subsidence). Cool colours mean motion toward the satellite. Say this in the legend, because the sign depends on the satellite geometry.

**Class breaks.** Use fixed, symmetric, hand-set breaks, not quantiles. Quantiles would stretch noise into colour, and the same colour must mean the same mm/yr in every view (E03 logic).
- Default clamp is +/-10 mm/yr. Offer a +/-20 option (EGMS-style) for fast sites. Anything beyond the clamp gets the end colour and the legend shows "<-10" and ">+10".
- Breaks (mm/yr):

| Class | Range | Role |
|---|---|---|
| 1 | < -10 | |
| 2 | -10 to -5 | |
| 3 | -5 to -2 | |
| 4 | -2 to +2 | stable band, neutral colour, drawn small and faint |
| 5 | +2 to +5 | |
| 6 | +5 to +10 | |
| 7 | > +10 | |

- The +/-2 mm/yr band is a starting default (synth). Set it from the measured velocity noise of the dataset, so it is not hard-coded. Slow landslides on roads are often only 5-20 mm/yr. A wider "stable" band would hide them.
- Show the break values on the histogram, with draggable handles (I05 widget "histogram with class breaks").

**Size and emphasis.** Keep the symbol size constant and small, about 4-6 px, growing with zoom. Stable points are small and low-opacity. Moving points (class 1-3 and 5-7) get a thin dark or light halo. The near-zero stops fail 3:1 contrast against the basemap by design, so the halo is needed (A06, A07).

**Not colour alone (A07).**
- Add a shape or ring for points over the threshold (for example a ring at |v| > 5 mm/yr).
- Give the table and legend a text label for each class: "Stable", "Slow", "Moderate", "Fast".
- Provide a table alternative to the map (A01) and keyboard operation (A02).

**Uncertainty (D08).** Velocity alone misleads, so use a second channel. Point opacity or a halo follows coherence or velocity standard error. Add a "Coherence >= X" filter slider, with the default set by the data provider's quality advice. Never mix heavily different quality levels without showing it.

**Density gaps.** Points exist only where the radar returns a stable signal, so forests, snow and steep shadow areas have none. Show this explicitly:
- Add an optional "no coverage / low coherence" hatched mask (E-layer, synth), or at least a note.
- Otherwise empty ground reads as "stable ground", which is the most dangerous misreading for engineers.

**Filters (top bar).** Orbit (ascending, descending, or both), velocity threshold, coherence, and date range or release. Keep the active filters visible as chips (I-rule on active filters).

## 3. Other layers

| Layer | Default | Symbology |
|---|---|---|
| PS velocity points | on | as above |
| Road centreline / assets | on | neutral dark line, 2-3 px, on top of the points. Segment colour is optional: max |velocity| within a buffer, in the same ramp and with the same breaks |
| Landslide inventory polygons | on | outline only (dashed, one dark hue) with a light 15% fill. Never use the velocity colours here, because that would confuse the two meanings |
| Interpolated velocity raster (if you must offer one) | off | same diverging ramp and breaks, 50-60% opacity, with a mask outside the valid area. Label it "interpolated, not measured" because it implies information between points that does not exist. |
| Vertical and east-west components | off | separate layers, each with its own legend. Do not mix them with LOS. |
| Acceleration | off | diverging ramp for change in velocity, with its own legend and title |
| Hillshade / slope | off | grey, under the points, to give terrain context |
| Basemap | on | muted, low-saturation, so the ramp stands out. Offer light, dark, and imagery. Switch the palette to the dark-basemap stops with the basemap. |

Layer order, bottom to top: basemap, hillshade, rasters or polygon fills, inventory outlines, roads, points, selected-feature highlight, labels (Y rules). Provide a layer panel with opacity sliders and a visible scale range, and note when a layer is hidden at the current zoom.

Zoom behaviour: at low zoom, show aggregated cells (max or median velocity, point count) or cluster, never thousands of overlapping dots (P rules). Use vector tiles with slim attributes (id, velocity, coherence, std). Fetch the time series on click, not with the tiles.

## 4. Legend
- Placed on the map, always visible, collapsible but never hidden by default. It follows the visible layers only and also lists hidden or empty ones as "off".
- Title: "Ground velocity along the satellite line of sight (mm/year)". Show the unit, the sign meaning ("away from satellite / toward satellite") and the clamp ends ("< -10" and "> +10").
- Include the stable band as a labelled grey-ish class, and the "low coherence / no data" swatch.
- Show the ring marker meaning, and "interpolated" for rasters.
- It lists the data source, the reference point, the period covered and the orbit.
- Attribution is visible on load (C01), including Copernicus Sentinel-1 data and the processor.

## 5. Click on a point (hover only highlights, I02)
Hover: change the cursor and highlight the feature, with a tiny tooltip at most (velocity value). Click opens a detail drawer on the right, or a bottom sheet on mobile, not a huge popup. Show curated, aliased, formatted fields with the title first (I04).

Content, top to bottom:
1. Title: "Point #id" with a plain verdict chip with icon and text: "Stable", "Slow movement", "Moving", "Fast" (from the same breaks).
2. Velocity: "-7.3 +/- 1.2 mm/year (away from satellite)". The +/- is the standard error.
3. Estimated vertical or downslope equivalent, if the project provides it. Clearly label it as an assumption, with the slope-direction assumption stated.
4. Time-series chart of cumulative displacement (mm vs date), with the points, the fitted trend line, and the acquisition-gap markers. Direct-label the series (D07). Flag or remove bad observations (T09 logic). Let the user brush a time range, which recalculates the velocity. Show an acceleration cue if the recent slope exceeds the long-term slope.
5. Quality: coherence, number of images, orbit, period.
6. Context: nearest road chainage or km marker, distance to road, whether it is inside a landslide polygon, and the number of neighbouring points that move together.
7. Actions: "Select neighbours / draw area to average" (click or lasso to average the series), "Zoom to", "Copy link" (URL carries the view and selection), "Export CSV".

Click on empty map: shows nothing. Click on a polygon: show the polygon stats (points inside, median and max velocity, area, source of the inventory). Click on a road segment: show the same stats for its buffer. The ranked table and the chart sync with selection both ways (D09, I05). The Escape key closes the drawer and keyboard focus returns to the map point.

## 6. What must be explained to non-specialists
Put a "How to read this map" panel, short and plain, linked from the legend. Cover these points.
1. **What it is.** Radar satellites revisit every 6-12 days. Comparing images gives how far each ground spot moved toward or away from the satellite. It is a measurement of change, not a photograph.
2. **Line of sight (LOS).** The satellite sees the ground at an angle (about 30-45 degrees from vertical). It measures only the part of the motion along that line. A slide moving along a direction perpendicular to the line of sight can look stable. Ascending and descending orbits see different components. This is the item flagged in the blueprint pitfalls (LOS shown to non-experts without explanation).
3. **Relative, not absolute.** Velocities are relative to a reference point assumed to be stable. If the reference moves, everything shifts. Show the reference point on the map, and do not compare across large areas or different datasets.
4. **Sign and units.** mm/year, with the direction convention. Give scale: 10 mm/year is a 1 cm/year, slow, and still important for a road.
5. **Measurement points, not areas.** Points only exist on stable reflectors such as rock, buildings, road surfaces, and bare ground. Vegetation, snow and steep shadow areas have no points. No points does not mean no motion.
6. **Uncertainty and noise.** Show error bars. The "stable" band is a noise threshold. Atmospheric effects can create false trends over short series, so one point is weak evidence and a cluster is strong evidence.
7. **Not a landslide map.** A moving point is an indicator, not proof of a landslide. Confirm with field inspection, other data and engineering judgement. Slow, creeping movement is detected well. Sudden failures between acquisitions are not.
8. **Time.** The data covers a specific period, and the latest acquisition date and processing release should be shown (D02 freshness widget). Old results may not reflect today's behaviour.
9. **Accuracy limits.** Position accuracy is a few metres, and a point may belong to a structure beside the road, not the road itself.
10. **Interpolated rasters** (if shown) create information between points. Treat as a visual guide only.

Use plain wording first, with technical terms in parentheses and tooltips on first use. Include a one-line caveat in the drawer ("Relative motion along satellite line of sight; not a confirmed landslide").

## 7. Alerts and ranking
- Table of road segments or inventory polygons, ranked by max |velocity| and by acceleration, with count of moving points. Severity bands match the breaks (stable within about +/-2, moderate, high), with escalation on acceleration and on the number of assets hit.
- Clicking a row zooms and highlights it, and the table scrolls to the item selected on the map (D09).
- KPIs, each with units and a reference (D01): number of moving points, km of road on moving ground, max velocity, compared with the previous release.

## 8. Accessibility and performance
- Colour is never the only carrier (A07). Keyboard access to points through the table, and the Tab key leaves the map (A02, A03).
- Provide a text summary of the map (A01). Loading, empty, error and stale states for each widget.
- Slim tiles, clustering at low zoom (P rules).

## 9. Pre-delivery checklist
- [x] Diverging ramp centred on 0, symmetric clamp (S06)
- [x] Colour-blind-safe, no rainbow (S08, S09)
- [x] 7 classes, within the diverging limit (S04)
- [x] Fixed break domain and ticked legend (E03 logic)
- [x] Uncertainty channel (D08)
- [x] Shared selection (I05); hover highlight and click details (I02); curated popup fields (I04)
- [x] Icon, ring or label with every colour meaning (A07)
- [x] KPI with units and reference (D01)
- [x] Attribution on load (C01)
- To verify in implementation: contrast with the chosen basemap, the noise-based stable band, and the real reference-point location.
- Note: the palette, the +/-2 mm/yr stable band, the +/-10 clamp and the layer defaults are synth defaults from the blueprint, not from an authoritative standard.
