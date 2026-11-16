# Evaluation scenarios

Each scenario is run twice by a subagent: once told to follow `SKILL.md`, once as a baseline without it. Record which checks each run hits in `the matching `results-<version>.md``.

## Scenario 1: Vessel detection dashboard (Sentinel-1 + AIS)

### Prompt
> Design the UI/UX for a web dashboard that detects vessels in Sentinel-1 SAR imagery and cross-checks them against AIS. The users are maritime analysts watching a port and its approaches. Give me the layout, the map layers and their symbology, the controls, the legend, and the pitfalls to avoid. Do not write code; produce a design brief.

### Expected behaviours
- [ ] Detections with no matching AIS ("dark" vessels) are visually distinct from AIS-matched ones, using more than colour alone (shape, outline or icon).
- [ ] Recommends a detection confidence threshold control (slider) with the current value visible and a count of detections that updates.
- [ ] Shows the scene acquisition date/time (and age) of the SAR image on the map or in a panel.
- [ ] States the pitfall "dark does not mean illegal" (AIS gaps, transponder off, small vessels, matching tolerance) and words the UI labels neutrally (e.g. "no AIS match", not "suspicious").
- [ ] Mentions the AIS/SAR time offset: AIS positions are interpolated to the acquisition time, and the match radius is stated.
- [ ] Mentions SAR false-positive sources (look-alikes such as wind, wakes, rocks, ambiguities) and offers a way to review the evidence (image chip, details panel).
- [ ] Includes a legend that covers every symbol class, including "unmatched", and a per-layer source/provenance label.
- [ ] Proposes a list or table linked to the map (select a row, the map flies to the vessel).

## Scenario 2 (omitted)

A review of a screen in a private app. Its prompt, expectations and raw runs are not part of the public repo.

## Scenario 3: Symbology for an InSAR landslide app

### Prompt
> I am building a web app that shows InSAR ground-motion results (Sentinel-1 persistent scatterers, mm/year velocity) to help engineers find slow landslides on a mountain road corridor. Choose the symbology and the interaction design for the velocity points and any raster or polygon layers: colour scheme, class breaks or scaling, legend, what happens when a user clicks a point, and what must be explained to non-specialists.

### Expected behaviours
- [ ] Uses a diverging colour ramp centred on zero (no motion), not a sequential ramp such as viridis or a rainbow.
- [ ] Uses a symmetric clamp, such as +/-N mm/year, so that equal motion toward and away gets equal colour weight. The legend shows the clamp values and says that values beyond them are clipped.
- [ ] Shows a per-point displacement time series (a chart on click) and not only the mean velocity.
- [ ] Explains line-of-sight (LOS): motion is measured along the satellite look direction, so positive means toward or away from the satellite, not vertical or downslope. Gives the ascending/descending caveat.
- [ ] States the reference point and the time span of the analysis, and notes that velocities are relative to the reference.
- [ ] Mentions coherence or quality filtering, such as a coherence slider, and the fact that there are no points on vegetation or decorrelated areas (absence of points is not stability).
- [ ] Warns against rainbow ramps, and picks a colourblind-safe diverging scheme.
- [ ] Recommends context layers, such as slope, a landslide inventory or roads, and a way to compare points with them.

## Scenario 4: Civic service-requests map for residents

### Prompt
> A city council wants a public web map where residents can see reported problems (potholes, broken lights, blocked drains) and follow their status. Many users are older and on phones. Propose the visual design and interaction: look and feel, how requests and statuses are drawn, what a click shows, and anything we must be careful about. Do not write code; produce a design brief.

### Expected behaviours
- [ ] Brings in a deliberate, restrained visual character (a named direction), kept subtle for a public civic audience, rather than a generic default.
- [ ] Offers a plain, safe baseline option next to any more distinctive direction.
- [ ] Status (open, in progress, resolved) is encoded with more than colour alone (icon, shape or text label) and the legend covers every status.
- [ ] Personal data (reporter name, phone, address) is hidden from the public view and omitted from the query and export, not only hidden in the UI.
- [ ] Popup or detail content is rendered as text, not raw HTML from data.
- [ ] No bold or decorative motion; states a reduced-motion path (prefers-reduced-motion) for any animation.
- [ ] Map attribution stays visible on load and findable after collapsing.
- [ ] Touch targets and text sizes suit phones and older users, with contrast stated.

## Scenario 5: Fleet and maritime operations screen

### Prompt
> We are building an operations screen for a dispatcher who tracks about 300 vessels and service boats in a harbour region, with alerts, a list of vessels and a history view. Design the screen: layout, how the vessels are symbolised, what the dispatcher sees about data age and status, how history or replay works, and what to avoid. Do not write code; produce a design brief.

### Expected behaviours
- [ ] Offers two or more distinct visual directions and also a plain, neutral baseline option.
- [ ] Applies the distinctive element in the marker grammar (shape, heading, state encoding) or in a hero timeline/replay control, at a balanced level suitable for a working tool.
- [ ] Data colour ramps and class colours stay untouched by the style direction (referenced from palettes, not restyled), and control positions follow conventions.
- [ ] Shows data freshness per vessel or feed (last update time and age, stale state) with a UTC or explicit-zone time label.
- [ ] Status is encoded with more than colour alone and the legend covers each state.
- [ ] Handles density: clustering or declutter at low zoom, selection linked between list and map.
- [ ] Replay or history has play/pause, a scrubber, speed control and a visible current time.
- [ ] Motion (trails, pulses) is limited and has a reduced-motion alternative.

## Scenario 6: Pre-sales 3D site story with CesiumJS

### Prompt
> Our sales team wants a scroll-driven 3D presentation of a planned industrial site built with CesiumJS: camera flights between five stops, a terrain view, and a few labelled buildings and distances. It should feel impressive on a big screen. Propose the visual design, the interaction and the technical cautions.

### Expected behaviours
- [ ] Proposes a clearly expressive, cinematic look suited to a presentation, at a bold level, while keeping data readable.
- [ ] Keeps the Cesium credits and the Cesium ion logo visible (not hidden by CSS or option) and the data attribution intact.
- [ ] Provides a 2D or static fallback for devices without WebGL or with weak GPUs.
- [ ] Provides a reduced-motion path (prefers-reduced-motion): jump cuts or fades instead of long camera flights, with a pause control.
- [ ] Labels vertical exaggeration if terrain is exaggerated, and states that heights are exaggerated.
- [ ] Distinguishes distance types (straight-line, surface, ground vs 3D) for any measured distance and labels which is shown.
- [ ] Keeps navigation by keyboard and a non-scroll alternative (next/previous controls) for the stops.
- [ ] Mentions performance cautions (tileset load, level of detail, loading state).

## Scenario 7: Review of a synthetic map page

### Prompt
> Review `evals/samples/review-sample.html` for UI/UX and map-design problems. List each problem with where it is, why it matters and a fix. Do not rewrite the whole file.

### Expected behaviours
- [ ] Finds that attribution is disabled (`attributionControl: false`) and cites C01.
- [ ] Finds that `setHTML` is fed `feature.properties.note` (XSS risk) and cites I10.
- [ ] Finds that the popup shows owner name and phone number to every user, and cites I11.
- [ ] Finds the rainbow/jet-like colour ramp on raw counts and cites S08, and notes counts should be normalised or use a perceptual sequential ramp.
- [ ] Finds the local-midnight `startOf('day')` date filter sent without zone conversion and cites T10.
- [ ] Gives a concrete fix for each finding.
- [ ] Does not invent further defects as findings (optional low-severity remarks are labelled as such and not counted).
- [ ] Reports each finding with a location (line or code excerpt).
