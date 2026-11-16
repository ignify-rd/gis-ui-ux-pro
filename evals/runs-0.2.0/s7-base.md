# Review: review-sample.html

## Map design

1. **Rainbow ramp on a choropleth** (lines 54-55, `fill-color`)
   - Why: The blue, cyan, green, yellow, red ramp is not perceptually uniform. It fails for color-blind users, mainly the red/green pair. Its bright yellow and cyan bands read as false class boundaries. It is hard to read as ordered low-to-high.
   - Fix: Use a sequential, colour-blind-safe ramp such as YlOrRd, Viridis or Blues.

2. **Raw counts in a choropleth** (line 54, `['get','count']`)
   - Why: Counts depend on district size and population. Larger districts look worse, and the map misleads.
   - Fix: Normalise the value, for example requests per 1,000 residents or per km². Otherwise use proportional symbols for raw counts.

3. **Hard-coded stops at 0-240, linear interpolation** (lines 54-55)
   - Why: The stops are tied to this sample data. New data outside the range gets clamped. A linear ramp over skewed data (12, 87, 240) hides differences among low values.
   - Fix: Use a `step` expression with classed breaks (quantile or Jenks) that fit the data. Show 4-6 classes.

4. **No legend** (whole page)
   - Why: Users cannot decode the colours or units. The `count` property is never explained.
   - Fix: Add a legend with class ranges, units and the date it refers to.

5. **Fill opacity 0.7 with no outline** (line 53, only a fill layer)
   - Why: Colours are muddied by the basemap underneath. Adjacent districts have no visible borders, and labels are hard to read.
   - Fix: Add a thin `line` layer for district borders. Raise opacity to about 0.8-0.85 or lower it deliberately so the basemap reads. Add district name labels with a halo.

6. **No hover or selected state** (lines 46-68)
   - Why: Nothing signals that the polygons are clickable. The pointer does not change, and the clicked district is not highlighted.
   - Fix: Set the cursor to `pointer` on `mouseenter`. Use `feature-state` for hover and selected outlines.

7. **The attribution control is disabled** (line 41, `attributionControl: false`, with no replacement)
   - Why: This removes the required credit for the basemap and data. It is a licence and trust problem.
   - Fix: Remove the option, or add `AttributionControl({ compact: true })` with the proper credits.

8. **Demo basemap, unplanned initial view** (lines 38-40)
   - Why: demotiles is a world-scale demo style that has no detail at zoom 10 and no street context. The data sits at lon/lat 10, 10, in the ocean off Africa. The view is hard-coded rather than fitted to the data, so users may see nothing if the extent changes.
   - Fix: Use a real basemap with a muted palette so the thematic layer stands out. Call `map.fitBounds` on the data bounds with padding.

9. **Scale control is metric only, positioned at bottom-left** (line 44)
   - Why: This is minor. It is fine for a metric audience, but it may clash with the legend you add.
   - Fix: Choose control positions deliberately. Consider a locale-aware unit.

## Interaction, data and logic

10. **XSS through `setHTML` with feature data** (line 63)
    - Why: `note` comes from data, and `setHTML` parses it as HTML. A malicious or compromised value can run script.
    - Fix: Use `setText`, or build DOM nodes with `textContent`. Sanitise if HTML is really needed.

11. **Personal data in the popup** (lines 27-31, 65-67)
    - Why: The owner's name and phone number are shown to every visitor. This is a privacy and compliance problem, and the data does not need to be on the client at all.
    - Fix: Remove these fields from the payload. Show them only to authorised roles, and fetch them server-side on demand.

12. **The popup is built by appending to the element after `addTo`** (lines 62-67)
    - Why: This bypasses the popup content API. The `<p>` is attached to the popup wrapper, outside the content container, so it is styled badly, may sit over the close button and tip, and is lost on re-render.
    - Fix: Build one content node (title, note, contact) and call `popup.setDOMContent(node)` before `addTo`. The popup has no title, no district name, and no count.

13. **Filter result handling is broken** (lines 70-80)
    - Why: `loadRequests` returns point or request data, but `setData` overwrites the `districts` polygon source with it. The styling by `count` and the polygons will break or vanish. There is no `.catch` and no `r.ok` check, so failures are silent. There is no loading state and no empty state. Rapid changes cause race conditions. The `change` event never fires on initial load, so the page shows unfiltered data labelled with 2026-11-01.
    - Fix: Use a separate source for requests, or have the API return the same district aggregate. Handle errors with a visible message. Cancel in-flight requests with `AbortController`. Load the initial date on `load`. Show a loading indicator and "no results".

14. **Query string is not encoded** (line 77)
    - Why: ISO timestamps contain `+` or `:`, which can break parsing. Concatenation is fragile.
    - Fix: Use `URLSearchParams`.

15. **Timezone handling** (lines 71-73)
    - Why: `dayjs(...).startOf('day')` uses the browser's timezone, then `toISOString()` converts to UTC. The "day" can differ from the district's local day, so users in other zones get different results.
    - Fix: Send the plain date plus an explicit zone (the district's), and let the server compute the range. This also removes the dayjs dependency, which is an extra third-party script for little value.

16. **Unpinned CDN dependencies, no SRI** (lines 8-10)
    - Why: `@4` and `@1` float on major versions. A script from unpkg without `integrity` is a supply-chain risk. A single CDN failure breaks the app.
    - Fix: Pin exact versions with `integrity` and `crossorigin`, or bundle locally.

17. **Map `error` and style load failures are not handled** (lines 36-47)
    - Why: If the style or tiles fail, the user sees a blank page.
    - Fix: Add `map.on('error')` and a visible fallback message.

## UI and accessibility

18. **Filter panel** (lines 14, 18-21)
    - Why: It is a floating white box with no shadow or clear heading. It sits over the map at 8px, which is tight. It does not account for safe areas or the nav control. The fixed `z-index: 1` is fragile. The `<label>` is fine, but there is no explanation of what is filtered. The date input has no `min` or `max`, and a hard-coded default value.
    - Fix: Add a heading, a shadow, bigger touch targets of at least 44px, and `max` set to today. Default to today and use it consistently.

19. **Small touch targets and controls** (line 43, default MapLibre controls)
    - Why: The default controls are about 29px, below the 44px recommended on touch devices.
    - Fix: Enlarge them with CSS on touch screens.

20. **Keyboard and screen-reader access is missing** (whole map)
    - Why: Polygons can only be opened by mouse click, so keyboard and assistive-technology users cannot get the district data. Colour is the only encoding for the count.
    - Fix: Provide a table or list alternative of districts with counts, and a focusable list that opens the same popup. Add an `aria-live` region for load status. Add a text label with the count on the map.

21. **Missing `<main>` landmark, page heading and semantic structure** (lines 18-22)
    - Why: There is no `<h1>` and no landmarks, so the page is hard to navigate with assistive technology.
    - Fix: Add a visually hidden `<h1>` and landmark regions.

22. **Structural HTML issue** (line 1)
    - Why: The comment before `<!DOCTYPE>` triggers quirks mode in old IE. It is a minor issue in modern browsers.
    - Fix: Put the doctype on the first line.

23. **Small mobile points** (lines 12-14)
    - Why: The page uses `height: 100%` with `position: absolute`. On mobile browsers the address bar can cover content. The filter box can cover the map on narrow screens.
    - Fix: Use `100dvh` and size the panel responsively.

## Highest priority

Fix first: 10 and 11 (XSS and personal data), 13 (the data source is overwritten), 1-4 (colour ramp, normalisation, classes and legend) and 7 (attribution).
