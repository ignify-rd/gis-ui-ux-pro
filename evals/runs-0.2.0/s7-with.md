Problem:   service-requests (runner-up demographic-choropleth) - residents' requests aggregated by district
Layout:    map-first, one floating date filter, no legend, no list or text alternative
Direction: not evaluated (review only); safe baseline is Civic Paper, subtle
Hero:      none; the missing "what does a colour mean" legend should be the hero
Risks:     no attribution (C01) - raw counts in a choropleth (S01) - rainbow/red-green ramp (S08, S09) - unsanitised HTML popup (I10) - phone numbers shown to everyone (I11) - mouse-only map (A02)

Reviewed: review-sample.html (83 lines). Line numbers refer to that file. Rule ids come from the gis-ui-ux-pro knowledge base. Items marked "general" are general advice, not from the knowledge base.

## Critical

**1. Attribution is switched off (C01)**
- Where: line 41, `attributionControl: false`. No `AttributionControl` is added anywhere.
- Why: the basemap tiles (demotiles / Natural Earth / OSM-derived data) require visible credit. Attribution must be visible without interaction. It may collapse to an (i) button, but it has to stay findable.
- Fix: delete line 41 so the default control stays. Alternatively use `new maplibregl.AttributionControl({ compact: true, customAttribution: 'District data: City Council' })` at bottom-right. Keep it uncovered by panels (L11).

**2. Choropleth maps raw counts (S01)**
- Where: lines 54-55, `['get','count']` drives the fill. Districts of different size and population are compared by number of requests.
- Why: a large district looks "worse" just because it is large or populous. This is the classic choropleth error. Counts are totals, so they belong in proportional symbols (S02).
- Fix: use requests per 1,000 residents (or per km²). Compute `rate` server-side or in the properties, and label the legend with the unit. If you want totals, draw a circle layer at district centroids sized by `count`.

**3. Rainbow ramp with red/green and fully saturated hues (S08, S09, S10, S07)**
- Where: line 55, `#0000ff, #00ffff, #00ff00, #ffff00, #ff0000`.
- Why: it is a jet ramp. It has no perceptual order, so yellow reads "lighter" than cyan. It also uses green against red, which many colour-blind users cannot separate (A07). Saturated colours at 0.7 opacity fight the basemap.
- Fix: use a sequential, colour-blind-safe palette from the knowledge base (`-d palette`), for example ColorBrewer YlOrRd or YlGnBu with 5 classes. Choose explicit class breaks (`step`, not a smooth `interpolate`) so the legend can list them (S04, S05). On a light basemap, dark means high (S07). Mute the basemap so the data is strongest (S10).

**4. Popup injects data as HTML (I10)**
- Where: line 63, `popup.setHTML(feature.properties.note)`.
- Why: `note` is free text that comes from residents. Any markup in it becomes script injection (XSS) in the popup. The same file correctly uses `textContent` for the owner line (line 66), so the safe pattern is already there.
- Fix: use `popup.setText(...)`, or build DOM nodes with `textContent`. Only use `setHTML` for a trusted template, or after sanitizing the output.

**5. Personal data in the popup for everyone (I11)**
- Where: lines 27-31 (owner and phone sit in the client GeoJSON) and lines 65-67 (shown on click).
- Why: names and phone numbers are visible to any visitor. They are also in the page payload, so hiding them in the UI would not remove them.
- Fix: do not send `owner` or `phone` to the public client at all. Return them only to authenticated roles that need them, from a separate endpoint. Public popups show the district name, request count or rate, and a category summary.

**6. Map is mouse-only, with no text alternative or keyboard path (A01, A02, A03, A04, C09)**
- Where: the whole page. There is no `aria-label` on `#map`, no skip link, no table or list of districts, and the click handler (line 60) has no keyboard equivalent. The page has no search or coordinate input.
- Why: keyboard and screen-reader users cannot reach any district or its values. They cannot read the data at all.
- Fix:
  - Add `role="region" aria-label="Map of service requests by district"` on `#map`.
  - Add a short summary line plus a district table (name, rate, count) as the text alternative.
  - Put a skip link before the map.
  - Add a district list or `<select>` that opens the same detail view as a click (this also covers the drag alternative, C09).
  - Keep the visible focus outline.

**7. Colour is the only carrier of the value, and there is no legend (A07, S13, S14, S18)**
- Where: the `districts-fill` layer (lines 48-57). There is no legend element anywhere.
- Why: users cannot decode the colours, so the map has no meaning. There is no class for "no data" or "no requests" either, so a district with no data would look like a low value.
- Fix: add a minimal legend next to the map (L06). It should be a single column of the 5 classes with units, for example "Requests per 1,000 residents, [date]". Add a neutral grey/hatched "no data" class. Show the value as text in the popup and list as well.

## High

**8. Date range is built in local time without a zone (T10)**
- Where: lines 70-74, `dayjs(...).startOf('day')` formatted as `YYYY-MM-DDTHH:mm:ss`.
- Why: the string has no `Z` or offset, so the server may read it as UTC while the user meant local midnight. Results shift by the user's offset and can drop or double events near midnight. The default date at line 20 is also hard-coded.
- Fix: convert the local day start and end to UTC and send RFC 3339 with `Z`, using `start.toISOString()` or `dayjs.utc()`. Show times with an explicit zone label. Native `Date` is enough here, so you can drop the dayjs script (line 10), a request that adds latency and an unpinned dependency.

**9. Filter result is never loaded and cannot fail visibly (P04, P06, D02)**
- Where: lines 76-80 and the `load` handler (lines 46-58). `loadRequests` runs only on `change`; first load uses the hard-coded sample, not the picked date. There is no `.catch` and no `r.ok` check. The response from `/api/requests` is passed straight to `setData`.
- Why:
  - The control says "Reported on 2026-11-01" but the map shows something else until the user changes the date.
  - A failed fetch gives a silent, stale map.
  - There is no loading feedback.
  - There is no "last updated" stamp.
- Fix:
  - Call `loadRequests` once on load with the default date.
  - Check `r.ok` and show a per-layer error with a Retry button (P06).
  - Show a thin progress bar if the fetch takes more than about 1 s.
  - Show "Updated hh:mm UTC".
  - Make sure the endpoint returns the same district FeatureCollection shape.

**10. Popup is bare and focus is not managed (I04, A10)**
- Where: lines 60-68. The popup shows only the raw `note` text: no title, no value, no unit. The extra `<p>` is appended outside the popup content wrapper.
- Why: users do not learn which district they clicked or what the number is. A keyboard or screen-reader user gets no announcement.
- Fix: build one content node with the district name as title, the rate with its unit, and a couple of curated fields. Use `popup.setDOMContent(node)`, move focus into it and return focus on close.

**11. No visible boundary, hover or selection state (Y05, I02, I03, A06)**
- Where: only a fill layer exists (line 48). There is no `line` layer, no hover `feature-state`, and no pointer cursor on `mouseenter`.
- Why: fills at 0.7 opacity sit over the basemap with no outline, so the graphic contrast against it is weak. Adjacent districts blend together, and users cannot tell that the polygons are clickable.
- Fix: add a thin outline layer above the fill (white or dark grey at 3:1 against the fill). On `mousemove` set a hover `feature-state`, and clear it on `mouseleave`. Set `cursor: pointer` on enter. Add a stronger outline for the selected district. Put labels on top.

**12. Demo basemap is busy and there is no layer or scale logic (S10, S11, Y02)**
- Where: line 38 `demotiles.maplibre.org/style.json`; the fill layer has no `minzoom`/`maxzoom` and no district labels.
- Why: demotiles is for demos, with saturated land and country fills, so the thematic colours compete with it. District names are missing, so people cannot say what they are looking at.
- Fix: use a muted light basemap (for example an OpenFreeMap Positron style, keeping its attribution). Add district name labels that appear from the zoom where they fit. Set explicit zoom ranges when you add more layers.

## Medium

**13. The filter control is minimal and not responsive (L09, A11, A04, I09)**
- Where: lines 14, 18-21. A fixed `top:8px; left:8px` box with `z-index:1`, and a bare `<input type="date">`.
- Why: the target size and spacing are small for touch. There is no state such as "N of M districts shown" or a clear action, and there is no way to see the active filter at a glance. A fixed overlay offers no mobile layout.
- Fix: enlarge touch targets to about 44 px, add an `aria-live` summary such as "240 requests on 1 Nov 2026" with a reset, and use a bottom sheet below 768 px. Give the box a focus ring (A04).

**14. Time is a single day and gives no guidance (T04, T08)**
- Where: line 20 and the `change` handler.
- Why: users cannot see which dates have data, and one-day counts per district will be tiny or zero. Pasting a date with no data returns nothing without explanation.
- Fix: offer a range (7 or 30 days) with presets. Disable or mark dates without data, and show an explicit empty state ("No requests on this date").

**15. No state in the URL (I08)**
- Where: the whole script. Date, view and selection live only in memory.
- Why: views cannot be shared and are lost on reload.
- Fix: write `date`, `lng/lat/zoom` and the selected district to `location.hash` or the query string. Read them on load.

**16. Numbers and units are not localised (A12)**
- Where: counts are shown raw (lines 27-31); the scale uses `unit: 'metric'` fixed (line 44).
- Fix: format with `Intl.NumberFormat(navigator.language)`. Let the scale follow the locale (C06).

**17. Control placement is mostly fine, but check the controls (C04, C05)**
- Where: lines 43-44. Zoom at top-right and scale at bottom-left follow the conventions. The `NavigationControl` includes a compass although the map was never meant to rotate.
- Fix: pass `{ showCompass: false }` or set `dragRotate: false` and `touchZoomRotate: { around: 'center' }` to disable rotation. Keep the filter at top-left (C04).

## Low

**18. Page and title basics (L10, general)**
- Where: line 6 `<title>District requests</title>`; no visible heading or about text.
- Fix: add a short visible title and an "About this map" panel naming the data source, update time and what a "request" means.

**19. Unpinned, unverified CDN scripts (general)**
- Where: lines 8-10 use floating major versions (`maplibre-gl@4`, `dayjs@1`) without `integrity`/`crossorigin`.
- Fix: pin exact versions and add SRI hashes, or bundle the dependencies.

**20. Motion and animation (A09, A13, general)**
- Where: nothing animates yet, but the default `flyTo`/zoom easing and any future auto-play would apply.
- Fix: when `prefers-reduced-motion` is set, use `jumpTo` and pass `{ animate: false }`.

## Also consider (low, optional)

- Show a table view or a ranked district list next to the map and link it to the map selection (I05, D09).
- Offer a second layer for point-level requests with clustering and a layer toggle (S16, Y01).
- Add an export with title, legend, scale bar, source, date and attribution (D11).

## What already works

- Zoom control at top-right and scale bar at bottom-left follow the usual corners (C04).
- Owner line is added with `textContent` rather than HTML (a safe pattern, though the data should not be there at all, see 5).
- `lang="en"`, viewport meta and a `<label for>` on the date input are present.

## Suggested fix order

1. Restore attribution (1) and fix the popup (4, 5).
2. Normalise the data and replace the ramp (2, 3), then add the legend with a no-data class (7).
3. Add the text alternative, keyboard path and focus handling (6, 10).
4. Fix UTC dates, the initial load, loading and error states (8, 9).
5. Polish: outlines and hover (11), basemap and labels (12), filter control (13), then the medium and low items.
