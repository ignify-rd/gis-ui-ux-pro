Problem: service-requests (residents or staff viewing city issues by district)
Screen: a MapLibre choropleth of 3 districts with a date filter and a click popup
Result: 6 critical, 5 high and 6 medium/low findings. Ids refer to gis-ui-ux-pro rules. Line numbers refer to review-sample.html.

## Critical

1. **Attribution is switched off (C01).**
   - Where: line 41, `attributionControl: false`, and no `AttributionControl` is added later.
   - Why: the basemap tiles (demotiles / Natural Earth / OSM-derived data) need visible credit. The licence requires it, and users need to know where the data comes from.
   - Fix: remove that option so the default control shows. Alternatively add `new maplibregl.AttributionControl({compact: true, customAttribution: '...'})` at the bottom. It may collapse after it has been shown. Also put the data source in the legend (D10).

2. **The choropleth maps raw counts (S01).**
   - Where: lines 54-55, `['get','count']` is used directly. District sizes here are equal, but real districts are not.
   - Why: big districts look "worse" only because they have more people and more area. The map misleads.
   - Fix: normalize the value, for example requests per 1,000 residents or per km². Compute it in the data (`rate`) and style on that. If totals matter, use proportional symbols (S02).

3. **The ramp is rainbow and not colorblind-safe (S08, S09, S06).**
   - Where: line 55, `#0000ff, #00ffff, #00ff00, #ffff00, #ff0000`.
   - Why: a jet ramp has no perceptual order. Red and green are confusable for people with CVD. Highly saturated hues also fight each other.
   - Fix: use a sequential, CVD-safe palette from the data (for example YlOrRd or YlGnBu from palettes.csv) with 3-7 classes (S04). Use step classes (`step`) and one classification method (S05) rather than a continuous interpolation.

4. **Meaning is carried by color only, and there is no legend (A07, S13, S14).**
   - Where: the fill layer (lines 48-57). No legend element exists anywhere.
   - Why: nobody can read values from the colors. The map also fails WCAG 1.4.1.
   - Fix: add a single-column legend with units ("requests per 1,000 residents") and class breaks. Add direct labels (district name and value) or hatch/labels as a second channel. The legend must reflect the active date filter.

5. **Popup renders attribute text as HTML (I10).**
   - Where: line 63, `popup.setHTML(feature.properties.note)`.
   - Why: if `note` comes from citizens or an API (as `/api/requests` suggests), this is an XSS hole.
   - Fix: use `popup.setText(...)` or build DOM nodes with `textContent`. Use `setHTML` only for trusted templates.

6. **The popup exposes personal data to everyone (I11).**
   - Where: lines 65-67, owner name and phone number.
   - Why: the data is PII. It is also in the client bundle (lines 27-31), so anyone can read it in DevTools even without clicking.
   - Fix: remove it from the public payload. Return personal fields from the server only for authorised roles, and log access. For residents show only category and status.

7. **There is no keyboard or text alternative for the map (A01, A02, A03).**
   - Where: the `#map` div (line 22) and the click-only handler (line 60).
   - Why: features can be opened only with a mouse. Screen-reader users get nothing.
   - Fix: give the map an `aria-label` and a short summary with a district table or list as the alternative. Add a focusable list or table where Enter opens the same detail. Add a skip link before the map. Do not trap focus in the map. Make popup focus move into the popup and return on close (A10).

## High

8. **The data flow is inconsistent and the filter has no feedback (lines 70-80).**
   - Problems:
     - The date control is never applied on load, because `loadRequests` runs only on `change`. The map shows the hard-coded sample districts while the picker says 2026-11-01, so the display and the filter disagree.
     - `loadRequests` replaces the `districts` source with whatever `/api/requests` returns. If that is a list of requests rather than district polygons, the layer breaks.
     - There is no loading state, no error handler (`.catch`), no empty state, and no "N of M shown" or active-filter chip (I09, P-rules).
   - Why: it fails silently and the user cannot tell what they are seeing.
   - Fix: run the filter once on load. Keep districts as polygons and join aggregated counts by id (D03, aggregate on the server). Add a loading indicator, an error message with retry, and an empty state. Show a chip such as "1 Nov 2026 - 87 of 340 requests". Keep the date in the URL (I08).

9. **There is no freshness or date stamp (D02, D10).**
   - Where: nowhere on screen.
   - Why: users cannot tell if the counts are today's or old.
   - Fix: add "Updated 14:05" and the selected date or range near the legend.

10. **Time handling is fragile (T10).**
    - Where: lines 71-73, the local-day boundaries `startOf('day')` converted with `toISOString()`.
    - Why: the picker returns a local calendar date. The query becomes a UTC window shifted by the browser's zone, so users in different zones see different "days". Requests near midnight land in the wrong day.
    - Fix: decide the city's time zone. Send the plain date (`2026-11-01`) and let the server interpret it in that zone, or send RFC 3339 UTC with explicit zone. Label times with the zone. Also this loads dayjs from an unpinned CDN just for this. `new Date()` and `Intl` are enough.

11. **The basemap competes with the data (S10, A06).**
    - Where: line 38, the MapLibre demo style (saturated country fills), with 0.7 opacity saturated fills (line 53) on top.
    - Why: the demo style is for demos, not production. The overlay hides street and label context. Contrast of any text against the fills is unchecked.
    - Fix: use a muted light basemap (for example OpenFreeMap positron, keeping its attribution) and a district outline layer (`line`, 3:1 contrast) above the fill. Put labels above the fill (Y05). Check labels at 4.5:1.

12. **No no-data class and no scale range on the layer (S18, Y02).**
    - Where: the paint expression has no fallback for missing or null `count`. The layer has no `minzoom`/`maxzoom`.
    - Why: a district with no data is drawn as the lowest class (interpolate clamps), so "zero" and "unknown" look the same.
    - Fix: use `['case', ['==',['get','rate'],null], '#bdbdbd', ...]` and add a neutral "no data" legend swatch. Set zoom ranges when you add finer layers.

## Medium / Low

13. **No hover feedback (I02, I03).** There is no hover state and no pointer cursor, so users cannot tell the districts are clickable. Use feature-state for a highlight and `cursor: pointer`, and clear it on mouseleave.

14. **Popup content is not curated (I04, Y04).** It shows a raw `note` with no title, aliases or formatted values. Fix: district name as the title, then "Requests per 1,000", the total count, and the top issue type.

15. **Popup built the wrong way (line 67).** Appending a `<p>` to `popup.getElement()` puts it outside the content container and breaks the layout and close behaviour. Build one DOM node and use `setDOMContent`.

16. **No search or coordinate input (C09) and a thin shell.** The filter box is a lone floating control (lines 14, 18-21). Fix: add a place or district search, and group the filter, legend and details together (L06) in a panel on the reading-start side (L02). On mobile use a bottom sheet. Keep touch targets at least 44 px (A11) and make the date control labelled with more than "Reported on" (add the units or what is counted).

17. **No reduced-motion or attribution-safe z-order check (A13, L-rules).** `z-index: 1` on `#filter` is fine now, but any future panel should be tested over the map controls. Honour `prefers-reduced-motion` before adding `flyTo` for zoom-to-district (I06).

18. **Housekeeping.** Pin versions instead of `@4` and `@1` on unpkg (use an exact version with SRI). The data URL (line 77) concatenates unescaped strings, so use `URLSearchParams`. The default NavigationControl shows a compass on a non-rotating map (C05), so use `showCompass: false` if rotation is disabled.

## What passes
- Control corners follow convention (C04): zoom top-right and scale bottom-left.
- The scale bar uses a unit and no fixed ratio (C06).
- The date input has a real `<label for>`.
- Viewport meta and `lang` are present.

## Fix order
1. Attribution, XSS and PII (items 1, 5, 6).
2. Normalized data and a CVD-safe ramp with a legend (items 2, 3, 4).
3. Keyboard and text alternative (item 7).
4. The data-flow and time problems (items 8-10).
5. Basemap and polish (items 11-18).

Labels: the rule ids above come from the skill's rule list (quick-reference). Items 9, 10, 12 and 16 rely partly on `synth` defaults (D02, T10, S18, L02). Treat those as recommended defaults, not hard requirements.
