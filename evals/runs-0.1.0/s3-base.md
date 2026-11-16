# InSAR velocity symbology and interaction design (mountain road corridor, slow landslides)

## 1. Core decisions

- Data type: signed velocity (mm/yr) along satellite line-of-sight (LOS), relative to a reference point. Use a **diverging** scheme centred on zero.
- Primary task: find clusters of moving points near the road. So the design must suppress the stable majority and make coherent moving clusters pop out.

## 2. Colour scheme (points)

- Diverging, colour-blind-safe: **blue (towards satellite / uplift-ish, positive LOS) to light grey/neutral to red/orange (away from satellite / subsidence-ish)**. Avoid red-green. Suggested ramp: ColorBrewer RdYlBu reversed or a custom blue-grey-orange (e.g. #2166ac, #92c5de, #d9d9d9, #f4a582, #b2182b). The neutral class must be light grey, not white, so it stays visible on a basemap.
- Stable points: small, grey, 50-60% opacity. Moving points: larger, fully opaque, thin white halo for contrast on imagery or hillshade.
- Basemap: muted greyscale hillshade/terrain plus road line; no saturated imagery by default (imagery as a toggle, with halo on points).
- Sign convention caveat: the sign depends on the processor (LOS positive toward satellite is common). Show the convention in the legend and do not label as "up/down" without explaining.

## 3. Class breaks / scaling

- Use **fixed, symmetric, meaningful breaks**, not quantiles (quantiles would paint noise as hazard and make maps non-comparable between dates/areas).
- Sentinel-1 PS precision is roughly ±1-2 mm/yr, so the noise floor sets the neutral class:
  - Stable: |v| < 2 mm/yr (grey; label "no detectable motion")
  - Slow: 2-5 (light colour)
  - Moderate: 5-10
  - Fast: 10-20
  - Very fast: > 20 (darkest; note possible phase-unwrapping limits, as a few mm/yr per ~28 mm half-wavelength per 6-12 days caps what is reliable)
  - Both signs symmetrical (7-9 classes total). Clamp the ramp at ±20 (or ±30), with open-ended end classes.
- Allow the user to change the stable threshold (slider) and the stretch (±10 / ±20 / ±50), with defaults saved per project. Show histogram in the legend as an optional element.
- Make a second, optional **"significance" filter**: hide points with low coherence (e.g. < 0.7) or high velocity standard deviation, or fewer than N acquisitions. Default on, with a visible counter ("1,240 of 3,100 points hidden by quality filter").
- Size: encode quality (not velocity) subtly, or keep constant. Do not double-encode velocity with size and colour, other than a mild size bump for |v| above the threshold.
- Zoom-dependent: at small scale use density/aggregate (hexbin of mean or max |v|, or heatmap of moving-point count) to avoid overplotting; switch to individual points at about scale 1:25,000 or larger. Draw order: highest |v| on top.

## 4. Legend

- Always visible, collapsible, a continuous/stepped bar with the class labels in mm/yr and the words "away from satellite" / "towards satellite" at the ends, plus a "stable" label in the middle.
- Contains: unit (mm/yr, LOS), reference-point note, date range ("Mar 2017 - Oct 2025"), orbit and geometry (ascending/descending), count of visible points.
- One-tap "?" opens plain-language help (section 7).
- Raster and polygon layers get their own legend entries, each with its own title, so that ramps are never confused (see section 6).

## 5. Click interaction (point)

- Hover: lightweight tooltip with velocity and class only. Click: select, highlight (ring), and open a side panel (bottom sheet on mobile) rather than a popup that obscures the map.
- Panel contents, in order:
  1. Headline: "−8.4 mm/yr, away from satellite (moderate)" with ± uncertainty and a quality badge (good/fair/poor).
  2. **Displacement time series chart** (cumulative mm vs date), with the linear fit line, seasonal/noise band, and ability to hover values. Time series is the key to separating slow landslides (steady or accelerating trend) from seasonal/thermal/snow effects (oscillation) and noise.
  3. Stats: coherence, std dev of velocity, number of acquisitions, first/last date, height/elevation, geometry (asc/desc), incidence angle.
  4. Neighbourhood context: the mean velocity of points within a radius (e.g. 50-100 m), and number of moving neighbours, with a button "select neighbours" so that engineers judge clusters rather than single points.
  5. Distance to road, slope and aspect from DEM (the projected downslope velocity estimate is flagged as an estimate).
  6. If both ascending and descending exist: show both, and optionally the decomposed vertical/east-west components (only where both are available, labelled as derived).
  7. Actions: export CSV of time series, add to a note/flag "needs field check", copy link, compare with another point (overlay series).
- Also support box/lasso selection to show a mean time series for a group, which is more robust than a single point.
- Keyboard: points focusable via a list view of the top-N fastest points near the road; the panel is screen-reader labelled; never rely on colour alone (class text in panel).
- Time slider/animation: optional, to recolour points by displacement-since-date, which is useful for spotting acceleration.

## 6. Raster and polygon layers

- **Raster** (interpolated velocity surface, or mean coherence): interpolated velocity rasters can mislead since PS are sparse and absent in vegetation. Use the same diverging ramp but at 60% opacity, mask areas beyond ~100-200 m from any point (or low point density) with hatch/"no data", and label as "interpolated". Prefer to show coherence/point density as a separate grey sequential layer, so users see where there is no information. Hillshade/slope: grey sequential, below everything.
- **Polygons**:
  - Detected/mapped deformation zones (clusters): outline only, with a single hue (e.g. magenta/purple) separate from the velocity ramp; fill hatch or 15% opacity. Label with an ID and mean velocity. Click leads to a panel with area, point count, mean/max velocity, trend, and link to the component points.
  - Known landslide inventory/geology/susceptibility: categorical or sequential (single hue, e.g. browns/purples), always lighter and thinner than velocity points, which stay on top.
  - Road buffer/corridor: thin dashed outline, no fill. Road segments may be coloured by max nearby |v| as a hazard summary (sequential, labelled "indicative").
- Z-order (bottom to top): basemap/hillshade, raster, polygons (fill), road, points, selection, labels.
- Layer panel with toggles, opacity sliders, and a "reset to default" button; only one diverging ramp visible at a time by default to avoid confusion.

## 7. What must be explained to non-specialists

1. **It measures along the line of sight, not true ground direction.** Satellite looks at about 30-45 degrees from vertical, sideways; so it sees mostly vertical motion and little north-south motion. Sign: towards vs away from the satellite, not "up/down" or "downslope".
2. **Relative, not absolute.** All values are relative to a reference point assumed stable; if the reference moves, everything shifts.
3. **Points are not everything.** Points exist only where radar returns are stable (buildings, rocks, road structures, bare slopes). **No points does not mean stable**: vegetated and snow-covered slopes, steep and shadowed/layover areas have no data. Show coverage/gap layer.
4. **Slow only.** Cannot detect rapid or sudden failures (rockfall, debris flow) or movements above ~ cm per revolution; and it is not an early-warning system for fast events.
5. **Uncertainty.** About ±1-2 mm/yr noise; individual points can be noisy; consider clusters and time series; velocity is an average and can hide acceleration.
6. **Not every mover is a landslide.** Settlement, thermal expansion of structures, groundwater, seasonal effects, construction, and atmospheric artefacts also appear. Field verification is required.
7. **Geometry effects.** Slopes facing away from the satellite or moving mainly north-south may show underestimated or no motion; ascending vs descending differ.
8. **Resolution and timing.** Points are about 5 x 20 m resolution cells (Sentinel-1 IW), 6-12 day revisit; data end at a given date and are not real-time. Show "data to" date prominently.
9. Provide a short first-run guide (3 steps), a glossary tooltip for terms (LOS, coherence, PS, reference point, ascending/descending), a "How to read this map" panel, and a disclaimer: indicative screening tool, not a substitute for geotechnical investigation.

## 8. Defaults summary

- Diverging blue-grey-red, fixed symmetric breaks (±2, 5, 10, 20 mm/yr), stable grey at low opacity, quality filter on, aggregation at small scale, click opens a side panel with time series and neighbours, cluster polygons in a separate hue, interpolated raster masked and labelled, legend with sign convention, and a plain-language caveat panel.
