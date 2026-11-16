# Evaluation scenarios (0.1.0)

Each scenario is run twice by a subagent: once told to follow `SKILL.md`, once as a baseline without it. Record which checks each run hits in `results-0.1.0.md`.

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
