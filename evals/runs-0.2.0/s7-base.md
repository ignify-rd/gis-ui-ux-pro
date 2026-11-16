# Review: review-sample.html

## Map design

1. **Rainbow ramp on the choropleth** (lines 52-56). The `fill-color` goes blue, cyan, green, yellow, red.
   - Why it matters: a rainbow ramp has no perceptual order. Yellow and cyan look lighter than blue and red, so equal steps in count don't look equal. It fails for red-green colour blindness. Pure `#00ff00` and `#00ffff` are garish on a basemap.
   - Fix: use a sequential single-hue or perceptually uniform ramp (YlOrRd, Viridis). Use a colour-blind-safe palette with 5 or fewer classes.

2. **Raw counts on a polygon fill** (lines 24-34, 54). The data is counts per district, and the fill is coloured by the raw count.
   - Why it matters: the colour reflects district area and population, not risk. Large districts look worse. A choropleth should show a rate or density.
   - Fix: normalise (requests per 1,000 residents or per km²). If you keep raw counts, use graduated proportional symbols instead of fill.

3. **No legend, no title, no units** (whole page).
   - Why it matters: users can't tell what the colours mean, what is counted, or for which date.
   - Fix: add a legend with class breaks, the unit and the selected date. Add a map title or heading.

4. **Hard-coded stops and fixed 0-240 range** (line 55).
   - Why it matters: values above 240 clamp. The ramp is tied to this sample, and 0 to 60 gets a huge colour jump. Once the date filter changes the data, the scale becomes meaningless.
   - Fix: use `step` classes from quantile or natural-breaks breaks computed from the data. Update the legend when the data changes.

5. **Fill opacity 0.7 over the basemap, with no outline layer** (line 53).
   - Why it matters: the basemap labels and borders show through and muddy the colours. Adjacent districts have no boundary line.
   - Fix: use a lower-contrast basemap, add a `line` layer for borders, and put labels above the fill (`beforeId`).

6. **Attribution removed** (line 41).
   - Why it matters: `attributionControl: false` hides the required credit for the OpenMapTiles and OSM-derived data. This is a licence problem.
   - Fix: remove the option, or add `new AttributionControl({compact:true})`.

7. **Demo tiles style** (line 38).
   - Why it matters: `demotiles.maplibre.org` is a world demo with no street detail. It isn't suitable for district-level work at zoom 10, and it has no SLA.
   - Fix: use a proper basemap (a muted vector style) that has roads and labels at this scale.

8. **Initial view hard-coded, no fit to data** (lines 39-40).
   - Why it matters: a hard-coded centre and zoom may cut off the data. The sample districts span 10-10.2, so the centre is arbitrary.
   - Fix: use `fitBounds` on the data extent, with padding.

9. **No hover or selected state, no cursor change** (lines 60-68).
   - Why it matters: nothing signals that the districts are clickable.
   - Fix: add `feature-state` hover highlighting and `cursor: pointer` on `mouseenter` and `mouseleave`.

## Interaction and UI

10. **Popup contains only the note, and the district name and count are missing** (line 63).
    - Why it matters: the popup shows "Pothole near school" with no district or number. The data the user needs is on the map without context.
    - Fix: show the name, the count (with its unit and date) and the note, as structured markup.

11. **XSS through `setHTML`** (line 63).
    - Why it matters: `note` is user-reported text rendered as HTML. A request containing `<img onerror=...>` runs script in the page.
    - Fix: use `setText`, or build DOM nodes with `textContent` (as is already done for the owner line), or sanitise.

12. **Personal data exposed** (lines 27-31, 66).
    - Why it matters: the popup shows each owner's name and phone number to every visitor. This is a privacy and compliance risk, and it's probably not needed for this use.
    - Fix: remove it from the client payload, or show it only to authorised roles.

13. **Popup is built by appending to `getElement()`** (lines 65-67).
    - Why it matters: this is fragile. `getElement()` is the whole popup container, so the paragraph lands outside the content wrapper and gets no padding or styling. The popup also isn't reliably built for repeat clicks.
    - Fix: build one content node (or a template) and pass it to `setDOMContent`.

14. **Click handler bound before the layer exists** (lines 60 and 46-58).
    - Why it matters: this works because the handler is delegated by layer id, but a click on a map with no layer throws no error and gives no feedback. There is also no handling for overlapping features or for clicks on empty areas.
    - Fix: register the handler inside `load`, and keep one popup instance that is reused and closed.

15. **Date filter has no feedback or error handling** (lines 70-80).
    - Why it matters: there is no loading state, no empty state and no error state. `fetch` has no `.catch` and no `r.ok` check. A failed request leaves the map stale and the user unaware. An empty `value` (a cleared input) gives an invalid date.
    - Fix: show a loading indicator, check `r.ok`, show an error or "no requests" message, and ignore an empty value.

16. **Filter control and the date semantics** (lines 18-21, 70-74).
    - Why it matters: the initial value `2026-11-01` is never applied on load, so the map shows the unfiltered state while the control claims a date. The timezone is also ambiguous: the range is formatted without an offset, so the server and client may disagree about the day.
    - Fix: call `loadRequests` on load with the default date, send ISO strings with the offset or UTC, and show the active filter in the UI.

17. **The API response replaces the district polygons** (line 79).
    - Why it matters: `setData(data)` assumes the endpoint returns the same district FeatureCollection. If it returns request points, the fill layer silently renders nothing.
    - Fix: keep the geometry and join the counts by id, or use a separate point source. Document the response shape.

18. **Query string is not encoded** (line 77).
    - Why it matters: the values are concatenated by hand. This is fine for these formats, but it breaks as soon as an offset (`+`) is added.
    - Fix: use `URLSearchParams`.

## Layout, accessibility and responsiveness

19. **Filter panel stacked against the map controls** (line 14, 43).
    - Why it matters: the panel is absolutely positioned at 8px with `z-index:1` and no shadow or border. It has tiny padding, and it has no heading. It may overlap popups and the controls on small screens. 4px radius and no elevation make it blend into the map.
    - Fix: use the MapLibre control position pattern or a proper panel with a shadow, spacing of 12-16px, and a safe-area margin.

20. **Touch targets and keyboard access** (lines 14-21, 43).
    - Why it matters: the date input is small, and the map's polygons can't be reached by keyboard. Screen-reader users get no equivalent of the choropleth.
    - Fix: enlarge controls to 44px, add focus styles, and provide a data table or list alternative with the same counts. Add `aria-label` to the map region.

21. **Colour-only encoding** (lines 52-56).
    - Why it matters: the information is conveyed only through colour.
    - Fix: add count labels on the districts (a `symbol` layer) and the table from item 20.

22. **Unneeded dependency and CDN fragility** (lines 8-10, 71-73).
    - Why it matters: `dayjs` is loaded for one `startOf('day')` and `add`. Unpinned major versions from unpkg with no SRI hashes can change under you or be tampered with. The page has no offline or fallback behaviour.
    - Fix: use native `Date` or a plain string (`value + 'T00:00:00'`), pin exact versions and add `integrity` and `crossorigin`.

23. **Minor** — the page has a vague `<title>`, and the HTML comment sits before the doctype (line 1), which puts older browsers in quirks mode.
    - Fix: move the comment below the doctype, and use a descriptive title and a visible heading.
