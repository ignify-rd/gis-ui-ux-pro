Problem:   site-suitability (closest playbook; this is really a pre-sales story, so I used its bold overlay) - a planned industrial site shown to prospects
Layout:    full-bleed 3D globe, a narrow story rail on the left, a stop indicator on the right, and a visible 2D/overview toggle
Direction: Urban Twin, bold (alt Canvas Studio at balanced; baseline Civic Paper, i.e. the same layout with the signature removed)
Hero:      orbit tour on arrival, with a time-of-day lighting preset tied to the site's real location
Risks:     scroll-jacking and keyboard traps (A02/A03) - motion sickness (A13/cs-09) - Cesium ion credits hidden by the UI (C01/cs-01) - silent vertical exaggeration (cs-02) - mislabelled distances (cs-03) - GPU load on the sales laptop

Assumptions, since nobody was available to ask. The audience is prospects and executives in a meeting room or at a trade show, with a salesperson driving. The screen is a 4K display or a projector, fed by one known machine that is probably also used in the field. The feeling is "impressive, but trustworthy". There is no brand palette, so I propose one accent. The basemap and terrain data come from Cesium ion or your own tiles, and the site model is a glTF or 3D Tiles tileset. Correct any of these and I will change the proposal.

## 1. Visual design (Urban Twin, bold)

The knowledge base has no "scrollytelling" playbook. The Urban Twin direction (synth evidence, so these are recommended defaults, not sourced facts) is the best fit: immersive, 3D buildings, orbit camera, a lighting preset as the hero. Tokens below are taken from it and adapted to Cesium.

| Zone | Proposal |
|---|---|
| Globe and terrain | World terrain on and imagery muted (low saturation, slightly dark), so the site is the brightest thing (S10). Soft atmosphere, a hint of fog at the horizon. |
| Site | The planned buildings are lit and slightly emissive. Surrounding context buildings are desaturated grey. The site footprint gets a thin outline. |
| Lighting | Hero: sun position tied to the site's real coordinates, set to golden hour or dusk for the flythroughs. Use `viewer.clock` plus `scene.globe.enableLighting`. Keep one fixed preset per stop, and do not run a day-night cycle on a loop. |
| Panels | Solid, 8px radius, 4.5:1 text. Glass only over sky, never over imagery (A14), with a "reduce transparency" option. |
| Type | Inter variable, single family. Big numerals for distances (60-80 px at 4K), titles of at least 48 px, and body text of at least 28 px for the back of the room. |
| Accent | One accent, for example a warm amber. It must not reuse any data-ramp hue (S19). |
| Markers | Building-anchored markers: a pin with a stem standing on the roof, a number matching the stop, and a label. Use `heightReference` and `disableDepthTestDistance` so buildings do not hide them. |
| Motion | 400-700 ms for UI, easing cubic-bezier(0.4,0.14,0.3,1). Flights of 3-5 s, eased in and out. Reduced motion means a static oblique view. |

Sketch (16:9):

```text
+--------------------------------------------------------------+
| 01 Arrival                                      o o o o o  <- stops
|  [rail]                                                       |
|   |   3D oblique view, site lit, labels anchored to roofs     |
|   o   "Warehouse A  42,000 m2"                                |
|   |        |<---- 380 m straight line ---->| Rail spur        |
|   o                                                           |
|  [Skip story] [2D map] [Terrain x1.0] [pause]     credits (C01)|
+--------------------------------------------------------------+
```

Safe baseline (it ships if the signature is cut): the same rail and stops, plain imagery, default markers, solid panels, no lighting preset, no orbit.

## 2. The five stops

Suggested order (replace with your real ones), one idea per stop:
1. Region context: the site in its logistics network (highways, port or rail, nearest city).
2. Approach: the access route, lit as a single line.
3. Terrain view: relief and grading, shown flat first and then with the terrain ramp. This is where exaggeration is used (see cautions).
4. Site overview: oblique with all labelled buildings and a footprint outline.
5. Detail: the key building, a close orbit, then a call to action (contact, data pack).

Each stop has an id, a camera pose (lon, lat, height, heading, pitch, roll), a duration, a title, 1-2 lines of text, and the labels to show. Store them as plain data, not as code branches, so sales can edit the order.

## 3. Interaction

- **Scroll as a scrubber for stop-to-stop, not as a free camera.** One notch or one gesture advances to the next stop, then a flight plays (`camera.flyTo`) with a fixed duration. Do not map scroll pixels to camera position. Cesium's camera is not cheap to move per frame, terrain tiles stream in late, and a trackpad produces thousands of tiny events. Debounce the input and ignore scroll during a flight, or queue only the latest one.
- **Do not hijack the page.** Use a dedicated full-screen stage (`overscroll-behavior: contain`) rather than a long scrolling page with a sticky canvas. The presenter can always go back.
- **Equivalent controls for every gesture.** Arrow keys and Page Up/Down move between stops, number keys 1-5 jump, a clicker or remote works (these send Page Up/Down), and the rail dots are clickable. Cesium's default mouse control stays available in a "free look" mode that the presenter enters on purpose, with a clear "back to story" button. No keyboard trap, and a skip link before the map (A02, A03, C08).
- **Presenter mode.** One key hides the UI chrome. Another key shows a small shortcuts overlay. An idle slow orbit after 20 s on the final stop is optional and needs a pause control (A13).
- **Mouse and touch.** Hover shows a building's name, click opens a short card (title first, curated fields, I04). On a touch wall, a swipe maps to next/previous stop.
- **Search or coordinate entry** is not needed for the story. Keep a stop list so any location can be reached without dragging (C09).
- **Prefers-reduced-motion** (A13, cs-09): `camera.setView` instead of `flyTo`, crossfade the text, no orbit, no looping animation. Test with the OS setting on.

## 4. Labelled buildings and distances

- Labels should come from the data (name, area, use), each with a leader line. Keep them short, white or dark text on a solid chip, halo at most one quarter of the font size, and check 4.5:1 against both terrain and sky (S20).
- Fix label size for the back of the room, and scale with `scaleByDistance` and `translucencyByDistance` so they fade out rather than collide. A maximum of 4-5 labels per stop.
- Distances: draw the line on the terrain (`clampToGround`) and state the method in the label, for example "380 m straight line" or "1.2 km along the ellipsoid, ignores terrain" (cs-03). Use `Cartesian3.distance` for the straight line and `EllipsoidGeodesic.surfaceDistance` for surface distance. Neither follows the road or the terrain. If sales wants a driving or rail distance, it must come from a routing source and be labelled that way, because a spurious precision is the most likely thing a prospect will challenge.
- Meaning must not rest on colour alone (A07): use line style (solid, dashed) plus a text label.

## 5. Technical cautions (Cesium)

1. **Credits and the ion logo** must stay on screen and readable. Do not cover the `creditContainer` with the rail or buttons (cs-01, C01). Move your own UI, not the credits. This also matters for any terrain, imagery or photoreal tiles, which have their own attribution terms.
2. **Vertical exaggeration** (cs-02): `scene.verticalExaggeration` distorts relief. If you use it for the terrain stop, show a visible badge such as "Vertical exaggeration x2" and a reset to 1.0. A sales audience reads slopes as real, and a flat industrial site made to look hilly is a credibility risk. Prefer 1.0 and let a better camera angle do the work.
3. **Ground height vs camera height** (cs-04): if you show elevation, use `scene.sampleHeight` (when `sampleHeightSupported`) or `globe.getHeight`, and do not print `camera.positionCartographic.height` as an elevation. Place building anchors using sampled heights, not guessed ones, otherwise models float or sink.
4. **Flights over unloaded terrain.** Wait for tiles at the target stop before the text appears: check `globe.tileLoadProgressEvent` or `tilesLoaded`, and show a quiet "loading" state, not a blank patch. Pre-warm each stop in the background by calling `camera.setView` offscreen is not possible, so instead preload with a short, low flight on first load (a loading screen with a progress bar) or use `scene.requestRenderMode` carefully.
5. **Performance on the big screen.** Rendering at 4K multiplies fill cost. Set `viewer.resolutionScale` (1.0, or 0.75 as a fallback), turn on `requestRenderMode` with `maximumRenderTimeChange` outside flights, limit `maximumScreenSpaceError` (try 2-4), and cap `tileCacheSize`. Disable `fxaa` or enable it, whichever tests faster. Test on the actual machine and projector, not a developer laptop. GPU load on weak devices is the main Urban Twin pitfall.
6. **Offline and venue Wi-Fi.** A trade-show network will fail. Cache or self-host tiles if the terms allow, or fall back to a pre-recorded video of the flythrough for each stop. Show a clear error state with a retry, not a frozen globe (P-rules, loading and error states).
7. **3D must have a 2D path** (cs-06): a visible 2D/overview toggle (`SceneMode.SCENE2D` or a flat top-down view), and a static image fallback when WebGL is not available. Also expose a `show3dObjects` style toggle, because buildings hide markers.
8. **Accessibility basics.** A text summary of each stop and a list of the labelled buildings and distances (A01), for screen readers and for printing as a leave-behind. Focus visible on all controls (A02). No flashing. Reading order of the panels follows the stop order.
9. **Data honesty.** Mark planned buildings as "planned" (an outline, a label, or a "concept" badge), and show a date for the source data and the model (D02). Do not mix real and planned buildings in the same style.
10. **Time of day** is a mood, not a fact. If the lighting is not the real time, say "illustrative lighting" in small print, and keep shadows on to ground the model.
11. **Wall display specifics.** Test the 5-second read from 5-8 m, avoid thin lines (use 3 px or more), and use contrast of at least 4.5:1 for text and 3:1 for graphics (check on both terrain and sky).

## 6. Self-critique and open items

- Locked conventions unchanged: zoom, search and layers controls stay in their usual corners, click and drag work as expected, credits visible. Pass.
- Data colours: the only data colour is the accent. If you later add a ramp (for example a slope or suitability layer), take it from the palettes (a sequential ColorBrewer ramp) and keep the accent out of that hue. Not yet applicable.
- Reduced-motion path: specified. Contrast on the chosen basemap: specified as a rule but must be measured on the real imagery. Not yet verified.
- Signature removable: yes, the baseline works with the same layout and data.
- Not verified: no mock was built, no performance was measured, and the five stops are placeholders.

Recommendation: ship Urban Twin with the orbit tour only on the first and last stops, and the lighting preset at every stop. Test with the 5-second, preference (baseline vs primary), first-click and squint tests.
