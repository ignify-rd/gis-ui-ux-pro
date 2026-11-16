# Scroll-driven 3D site presentation (CesiumJS): proposal

Assumptions: a single industrial site, five stops, shown on a large screen (a meeting room or trade-show display) and also on a laptop. The sales team presents it, and prospects may also open it alone. Site data may be glTF or 3D Tiles models, or simple extruded footprints. Imagery and terrain come from Cesium ion or an equivalent source.

## 1. Visual design

**Story first.** Five stops form one narrative, for example: 1 Region and access (highways, port, rail) → 2 Approach to the site → 3 Site overview (terrain, boundary) → 4 Key buildings → 5 Close-up of the loading and expansion area. Each stop has one headline, one supporting sentence and at most two figures. The point of each stop is a single sales message, such as "40 min to port" or "12 ha, expandable".

**Look.**
- Use a restrained dark UI chrome and large type that stays readable from 10 m away. Aim for a minimum of about 28 px equivalent at 1080p, scaled with `vw`.
- Use one accent color for the site: boundary outline, labels and route lines. Everything else stays muted.
- Make the globe feel premium. Turn on terrain with lighting and soft atmosphere, and use a slightly desaturated imagery layer so the accent color stands out.
- Add subtle fog/sky and a time of day with a low sun (golden hour) so building shadows give depth.
- Outside the site, dim or desaturate the surroundings, for example with a mask polygon or a darker imagery tint.
- Highlight the planned buildings with a distinct color and a gentle outline (silhouette post-process), not a glow overload.

**Labels and distances.**
- Use a few labels only (3–6 per stop). Use screen-space labels with leader lines, anchored to the building and given a depth-distance fade, so they do not clutter.
- Show distances as polylines, with a measured value on a label at the midpoint, for example "Highway ramp 1.8 km". Animate the line drawing in as the stop is reached.
- Put building labels in HTML overlays (positioned with `scene.cartesianToCanvasCoordinates`) for crisp text and CSS animation, or use Cesium `LabelCollection` with a `disableDepthTestDistance` set so they are not hidden by terrain.
- Add a small legend and a scale bar. Add a north indicator if the map is rotated.

**Terrain view.** Stop 3 or 4 includes a terrain moment: tilt the camera to a low oblique angle, apply vertical exaggeration (about 1.5–2x, declared on screen as "terrain exaggerated") and optionally a hillshade or slope tint. For a grading-sensitive site, show the platform level versus the surroundings.

## 2. Interaction

**Scroll mapping.**
- A fixed full-viewport Cesium canvas sits behind a tall scroll container. Each stop owns a section, for example 100–150 vh.
- The scroll progress `p` (0 to 1 within a segment) drives the camera by interpolation. Do not call `flyTo` per scroll event. Instead, define keyframes (position, heading, pitch, roll) per stop and compute the pose with an eased interpolation (smoothstep or cubic in-out) on `requestAnimationFrame`.
- Interpolate the position in Cartesian space with a mid-point lift (a parabolic arc in height) for long hops, so the camera rises and descends like a flight. Interpolate heading with shortest-angle wrapping.
- Smooth the scroll value with damping (lerp toward the target), so a wheel notch or trackpad flick does not jerk the camera. Scrub both directions identically so scrolling back is exact.
- Use `camera.setView` per frame, not `flyTo`. Optional alternative: snap sections (`scroll-snap-type: y proximity`) and trigger a timed `flyTo` per section; this is simpler and robust but loses scrubbing.

**Navigation and control.**
- Show a progress rail with five dots and stop names, clickable to jump (animated with a time-limited tween).
- Keyboard: arrows, PageUp/PageDown and Space move between stops. Support a presenter clicker (usually PageDown).
- Provide a "free explore" toggle that releases the camera to normal mouse control and a "Back to tour" button that returns smoothly. Disable the default camera controller while the tour is in control (`scene.screenSpaceCameraController.enableInputs = false`) so wheel scrolling does not zoom the globe.
- Provide an auto-play mode (a timeline that advances by itself) for unattended screens and a pause on any input. Add an idle reset to stop 1 after a few minutes at a trade show.
- Reduced motion: if `prefers-reduced-motion` is set, switch to short cross-fades or quick jumps rather than long flights.

**Content choreography.**
- Text cards fade and slide in only when `p` is in the stop's window, and they never cover the site subject. Place them in the left or right third and flip the side to match camera heading.
- At each stop: camera arrives, then the boundary/building highlights animate, then labels and distances draw in. Keep the total beat per stop at 3–6 seconds.
- Keep the camera always moving a little (slow orbit drift) at rest so it feels alive, but cap it.

## 3. Technical cautions

**Performance (big screens mean 4K and large canvases).**
- Set `viewer.resolutionScale` and cap `devicePixelRatio` (about 1.5 on 4K) to protect frame rate. Test on the actual display hardware and cable (GPU, browser, fullscreen).
- Use `requestRenderMode: true` and call `scene.requestRender()` while animating, so an idle screen does not burn GPU. Take care that async tile loads trigger renders (`maximumRenderTimeChange`).
- Turn off what you do not use: skyAtmosphere effects if costly, `fxaa` versus MSAA choice (MSAA 4x is nicer on edges but heavier), shadows only for the site (limit the shadow map size and distance), HDR and bloom sparingly.
- Reduce tile load: tune `maximumScreenSpaceError` (about 2 to 4 for quality on a big display, trading with bandwidth), use `tileCacheSize`, and use compressed (Draco/meshopt/KTX2) models. Keep building models light (< a few MB each, low draw calls).

**Smoothness of flights.**
- Pre-warm tiles: before the presentation, run a hidden pass or call a preload over each stop's view (`camera.flyTo` with duration 0 off-screen, or `Cesium3DTileset` `preloadFlightDestinations`/`preloadWhenHidden`) so no stop shows blurry terrain when you arrive. Show a loading screen until the first view and each key stop's tiles settle (`globe.tilesLoaded`, `tileset.allTilesLoaded`).
- Do not move through terrain. Clamp camera height above ground using `scene.sampleHeight` or `sampleTerrainMostDetailed` for keyframes, and verify the arc never dips under terrain, especially with exaggeration. Terrain exaggeration also shifts everything: place models, labels and polylines using the exaggeration-aware height (`scene.verticalExaggeration`) or they will float or sink.
- Avoid the camera passing close to 3D tiles with missing detail. Keep pitch and altitude in a range that always shows good data.
- Keep a constant "up" and avoid roll except for planned effects. Watch for gimbal-like flips at pitch near -90 degrees; use -85 or so.

**Accuracy (sales claims).**
- Distances: use geodesic (`EllipsoidGeodesic`) or route distances rather than straight lines in screen space, and label each as "straight-line" or "by road". Clearly mark the data source and date. For a contract-adjacent claim, have the engineering team sign off.
- Planned buildings must be clearly marked as "planned / illustrative" with a small footer disclaimer. Make sure the heights, footprints and datum (ellipsoid versus orthometric/geoid height) are right, otherwise buildings float. Check coordinates (CRS conversion to WGS84) with at least two known points.
- Imagery and terrain licences and attribution: keep the Cesium and data-provider credits visible (the credit display must not be hidden, even if it is moved into a footer).

**Reliability for a live demo.**
- Network is the biggest risk at an event. Prepare an offline fallback: self-hosted tiles/terrain (a local server or a local cache of the site area) and an offline build, or a pre-recorded video of the full flight as a backup. Test the presentation with the Wi-Fi off.
- Pin versions (CesiumJS version and ion asset IDs), keep the ion access token restricted (allowed URLs and scopes), and do not ship a default token. Handle WebGL context loss (reload the scene) and show a clear error.
- Test browsers: Chrome/Edge on the presentation machine first, then Safari and Firefox. Test a mobile fallback: mobile GPUs struggle, so use a lower resolution scale and shorter shadows, or a simplified mode.
- Wheel/trackpad differences: normalize scroll deltas, as a mouse wheel, a trackpad with inertia and a clicker behave very differently. Prevent browser bounce and pull-to-refresh, and test with a presenter remote.

**Accessibility and content.**
- Contrast of text over imagery: use a translucent panel behind text. Provide text alternatives to the labels (the same content as a list), keyboard focus, and `aria-live` for the stop title.
- Do not rely on color alone for the buildings and routes.
- Localization: text in a content JSON (stops, labels, distances) so the sales team can edit it without code. Keep the camera keyframes in the same data file, with a small dev-only "capture current view" button to record a pose. This makes tuning flights fast.

## 4. Suggested build order

1. Load terrain, imagery and site models, and verify alignment and heights.
2. Capture five keyframe poses with the capture tool, then implement scroll-scrubbed interpolation with smoothing.
3. Add labels and distance lines per stop, then text cards and the progress rail.
4. Tune the look (lighting, tint, outline, terrain exaggeration).
5. Optimize and pre-warm, then test on the real big screen, add the offline fallback and a recorded backup video.

Open question for the team: whether a presenter will drive it (favor clicker/keyboard and auto-play) or prospects will scroll alone (favor a visible hint, "Scroll to begin", and the free-explore toggle). This design supports both.
