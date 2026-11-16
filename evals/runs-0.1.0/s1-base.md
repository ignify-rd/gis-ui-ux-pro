# Design Brief: Sentinel-1 SAR Vessel Detection and AIS Cross-Check Dashboard

## 1. Users and core tasks
Users are maritime analysts monitoring a port and its approaches. They are often on a desktop with a large or dual monitor, and sometimes in a dim ops room.

Core questions, in priority order:
1. Which vessels in this scene are not broadcasting AIS (dark candidates)?
2. Which AIS vessels did SAR not see, and why? Possible reasons are out of swath, moored near clutter, or small size.
3. Is this detection a real vessel or a false alarm (wind or wave clutter, ambiguities, wind turbines, platforms, ice)?
4. What changed since the last pass?

The primary workflow is: pick a scene, triage the unmatched detections, inspect each one, then disposition it (confirm, dismiss or escalate) and export.

## 2. Layout (desktop first, 3 zones plus a timeline)
- **Top bar (48 px):** AOI selector (port and approaches presets), scene/acquisition picker, UTC clock, data-freshness badge ("S1A pass 05:42Z, AIS to 05:50Z"), and the user menu.
- **Left panel (320 px, collapsible):** a Layers tab and a Filters tab.
- **Center:** the map takes at least 65% of the width. It carries a scale bar, cursor coordinates (DD and DMS toggle), a north arrow, and a basemap switcher. A swath-footprint outline always shows the extent of the active scene.
- **Right panel (360 px, contextual):** a triage queue by default. Selecting a target swaps it for the Target Detail card.
  - The queue is a sortable list with columns for ID, status chip, length estimate, confidence and distance to port. Hovering a row highlights the target on the map, and clicking a row flies to it.
  - The detail card shows a SAR chip (a 256 px crop at native resolution with a contrast toggle), the AIS track history, match diagnostics, attributes and an action row.
- **Bottom timeline (80 px, collapsible):** acquisition ticks over time. A scrubber sets the AIS time window, which is linked to the scene time. A step control moves between passes. A "±N min" tolerance handle sits around the SAR acquisition time.
- **Summary strip (above the map or in the top bar):** KPI counters that double as filters. They show Detections, Matched, Dark (unmatched), AIS-only and Needs review. Clicking a counter filters the map and the queue.

Tablet and narrow screens: the panels become drawers and the queue becomes a bottom sheet. This is secondary, because the primary use is desktop.

## 3. Map layers and symbology

Principle: the classification (match status) is encoded by color and shape together, never by color alone. Size encodes the estimated length, with limits so that symbols stay legible.

### Basemap and context
- Dark neutral nautical basemap by default (low-saturation, so overlays stand out), with a light option and an optional ocean/chart style. Bathymetry and shoreline are muted.
- Port overlays: berths, anchorages, fairways and traffic separation schemes, restricted areas, and the EEZ or territorial-sea line. These are thin dashed outlines, low opacity, and labeled only at close zoom.
- Land and coastal mask, drawn as a hatched or flat fill. Detections inside the mask are filtered out by default, with a toggle.

### SAR layers
1. **Sentinel-1 scene raster** (VV/VH, dB, grayscale). Controls: opacity, stretch (min/max dB or percentile), a polarization toggle, and a swipe/curtain tool against the basemap. It is off by default at wide zoom (a footprint is shown instead) and loads at zoom 9 and above.
2. **Scene footprint / swath** is a thin outline with a label (satellite, orbit, time, mode).
3. **SAR detections**:
   - Symbol: a hollow ring or diamond marker, centered on the detected position. Where size is estimated, an oriented rectangle (a heading-aligned bounding box) appears at high zoom.
   - Colored by match status (see below). Marker size is stepped (3 to 4 classes), not continuous.
   - A confidence cue: line weight or fill opacity scales with the detection score. Low-confidence detections are dashed.
4. **Detection confidence/uncertainty** (optional): a faint ellipse shows positional uncertainty. This matters because SAR positions are offset for moving vessels (azimuth shift).

### AIS layers
5. **AIS positions** are solid filled triangles or arrow shapes oriented to course over ground (COG). They are interpolated or extrapolated to the SAR acquisition time, and a distinct "ghost" style marks extrapolated points.
6. **AIS tracks** are thin polylines with a fade-out by age. Only the selected target's track and tracks of the filtered set are shown.
7. **AIS time-offset line:** a thin line from the last reported position to the extrapolated position at the SAR time.
8. **AIS vessel type** is a secondary encoding (an inner glyph or a small icon at high zoom, otherwise no per-type colors). It is available through filters and in the popup.

### Match layer
9. **Match links:** a thin connector between a SAR detection and its matched AIS position. Line style shows the match quality (solid = strong, dashed = ambiguous). The distance in meters is a label on hover.

### Status palette (colorblind-safe, tested on dark and light basemaps)
| Status | Meaning | Color | Shape |
|---|---|---|---|
| Matched | SAR detection and AIS agree | Teal/cyan | Ring + filled AIS triangle, linked |
| Dark (unmatched SAR) | No AIS within the gate | Magenta/orange (high-salience) | Thick ring, with a pulsing halo only on first appearance |
| AIS-only | AIS expected in swath, not detected | Blue/grey | Triangle with a hollow center |
| Ambiguous | Several candidates in the gate | Amber | Ring with a "?" or split style |
| Suspected false alarm | Low confidence, or clutter flagged | Neutral grey, dashed | Small dashed diamond |
| Dispositioned | Confirmed / dismissed | Muted, with a check or cross glyph | -- |

Keep the high-salience color for dark vessels only. If everything is bright, nothing stands out.

### Clustering and scale
- Cluster by status at wide zoom, with counts and a status breakdown. Avoid heat blobs for operational targets.
- Label priority: dark and ambiguous first. Labels are shown for MMSI or ID and name only at close zoom or on hover.

## 4. Controls

### Layers panel
- Toggle and opacity for each layer group (SAR raster, detections, AIS, tracks, match links, port overlays, land mask).
- Reorder is not needed. A fixed, sensible z-order is enforced: raster < overlays < tracks < AIS < detections < selected.
- Basemap switcher and a "reset view to AOI" button.

### Filters
- Status (multi-select chips), confidence slider, length range (m), AIS vessel type, flag (searchable), speed range, distance to port or inside a zone (polygon/zone picker), and a reviewed/unreviewed toggle.
- Active filters show as removable chips above the map, so analysts never wonder why a vessel is "missing". A "N hidden by filters" notice is always visible.

### Matching parameters (analyst-adjustable, with defaults)
- Spatial gate (m) and time tolerance (min), with an auto-suggestion based on vessel speed and length. The default is shown, plus a "reset" button.
- Changing parameters shows a live count delta ("Dark: 14 -> 9") and the map updates. The change is recorded in the audit trail.
- Toggle for extrapolating AIS to the SAR time (on by default), and a stale-AIS cutoff.

### Time
- Scene picker with a calendar/ticks showing the coverage of passes and data gaps. Compare mode: two passes side by side or a swipe, with new, persistent and departed targets highlighted.
- AIS playback (play/pause, speed) around the acquisition time.

### Map tools
- Measure (distance and bearing), draw AOI, search (MMSI, name, IMO, target ID, coordinates), copy coordinates, a "locate" button, and a screenshot or export of the view.

### Target actions
- Confirm vessel, Mark as false alarm (with reason: clutter, wave, turbine, ambiguity, other), Flag/escalate, Add note, Assign, Link to AIS manually, and Export (CSV, GeoJSON, PDF report with the chip). Keyboard shortcuts (J/K next and previous in queue, C confirm, X dismiss, F flag) allow fast triage.

## 5. Legend
- Always visible but collapsible, anchored at the lower left of the map. It shows the status symbols with the labels and live counts, so it works as a clickable filter.
- Includes size classes (length bins), the confidence encoding (solid vs dashed), the AIS extrapolation ghost style, link styles, and the raster dB scale bar (when the raster is on).
- Legend entries reflect only the layers that are on.
- Plain-language definitions in tooltips, for example "Dark: no AIS report within 500 m and 30 min of the SAR time".

## 6. Target Detail card (content)
- Header: status chip, target ID, and detection time.
- SAR chip with linear/log contrast toggle and scale bar. Measurements show estimated length and width, heading (with a 180 degree ambiguity flag), and a peak/mean backscatter value.
- Detection confidence, with the main reasons for it.
- AIS match: MMSI, name, IMO, type, flag, dimensions, speed, course, last report time, age relative to the SAR time, and offset distance. A mini track plot.
- Why the status was assigned, in plain terms ("nearest AIS 1.8 km, outside the 500 m gate").
- Context: inside a port, anchorage or restricted zone, near a platform or turbine, and the history of passes at this location.
- Action row and notes/audit log.

## 7. States and feedback
- Loading skeletons for the queue and chip. A scene processing status with ETA when new passes are ingesting.
- Empty states that explain why ("No detections in this AOI for this pass. Swath covers 62% of the AOI.").
- Data-quality banners: stale AIS feed, AIS coverage gaps (terrestrial only vs satellite AIS), partial swath coverage, and low wind or high wind advisories that change detection reliability.
- Errors: clear, non-blocking, with a retry.

## 8. Accessibility and ops use
- WCAG AA contrast, shape in addition to color, keyboard-navigable queue and map controls, visible focus, and reduced-motion respect (the pulse can be turned off).
- Dark theme default for ops rooms, with a light theme. All times in UTC, with an optional local-time toggle that is always labeled.
- Units: meters, nautical miles and knots, switchable.
- Performance: vector tiles or server-side clustering for large AIS volumes, and progressive raster loading (COG/tiles).

## 9. Pitfalls to avoid
1. **Treating "unmatched" as "dark vessel".** Unmatched can mean a false alarm, an AIS gap, a stale AIS report, a small vessel without AIS class A, or a mis-registered position. Use neutral wording such as "Unmatched detection" with a confidence and a reason, and reserve "suspect" for analyst-confirmed cases.
2. **Ignoring the time offset.** SAR and AIS are not simultaneous. Always interpolate or extrapolate AIS to the acquisition time, show the offset, and let the analyst change the tolerance.
3. **Ignoring SAR geometry.** Moving vessels are displaced in azimuth (the offset can be hundreds of meters). Heading from SAR has a 180 degree ambiguity. Ghosts and ambiguities near strong reflectors give false targets. Show uncertainty, not false precision.
4. **Red-green or color-only coding.** Use a colorblind-safe palette with shape redundancy. Don't use red for both "dark" and "error".
5. **Too many bright symbols.** If every layer is saturated, dark targets don't stand out. Mute context and keep salience for exceptions.
6. **Hidden filters.** Silent filtering makes analysts think a vessel is missing. Always show active filters and hidden counts.
7. **Clutter at port.** Dense berths produce hundreds of overlapping markers. Use clustering, a land and berth mask, an optional "exclude moored" filter, and a zoom-dependent symbology.
8. **Raster overwhelming the map.** Use opacity defaults, a basemap swipe, stretch controls, and load rasters only at working zoom.
9. **Mixed time zones and stale data.** Always show UTC, scene time, and AIS age. Don't present old AIS as live.
10. **Unexplained automation.** Show why a match or classification was made, and let analysts override it. Keep an audit trail of overrides and parameter changes.
11. **Overloaded popups.** Use the side panel for details, and keep the map hover to a short tooltip.
12. **Fixed continuous symbol sizing.** Tiny vessels vanish and large ones swamp. Use stepped sizes with min/max pixel limits.
13. **Alert fatigue.** Avoid constant pulsing, sound, and notification spam. Prioritize the queue by risk and confidence instead.
14. **Wrong coordinate or datum display.** Label the CRS, and provide DD/DMS/DDM options. Check antimeridian and polar handling for global use.
15. **No coverage awareness.** An empty area could be outside the swath or lacking AIS reception. Always display swath coverage and AIS reception quality.
16. **Pass-to-pass comparison without alignment.** Compare only like-for-like acquisitions (same orbit and mode where possible), and flag differences in geometry.

## 10. Suggested validation
- Run a test with 3 to 5 analysts doing a timed triage task on a historical scene with known ground truth. Measure time per target, false-dismissal rate, and whether they correctly distinguish "unmatched" from "confirmed dark".
- Check legibility of the palette with colorblind simulations on both themes.
- Test density with a busy-port scene (500+ AIS and 100+ detections).
