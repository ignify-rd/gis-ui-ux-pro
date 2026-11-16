# Harbour dispatcher screen: design brief

```text
Problem:   maritime-awareness x fleet-tracking (blend) - ~300 vessels and service boats, one harbour region
Layout:    ops dashboard: map-first, list right, alert strip, history dock at bottom; no mobile (desk/ops room)
Direction: Signal Track, balanced (alt Night Ops; baseline Civic Paper with signature removed)
Hero:      replay scrubber docked under the map
Risks:     stale position shown as current (D02) - colour-only status (A07) - alert fatigue - rendering all history at once
```

## Assumptions (no one to ask)
- Users: dispatchers at a desk or ops-room monitor, long shifts, who need to see changes at a glance. Not a public or wall display.
- Feeling: calm watch, fast when something is wrong.
- Data: AIS or GPS positions at irregular intervals. Some service boats may report only via radio or their own tracker. About 300 objects, so no vector-tile or heavy clustering problem. Per-object history is fetched on demand.
- No brand constraints. Library not given. The brief is library-neutral, and every point holds for MapLibre, OpenLayers or Leaflet.
- Blueprint matching: the maritime-awareness playbook (score 11.1) fits the vessel and zone side. The fleet-tracking playbook (16.3) fits the dispatch side (stale pings, status, replay, alerts). This brief uses both. "Dark vessel" and SAR content is dropped unless you have satellite data. Items marked (synth) below are recommended defaults, not sourced facts, and you can override them.

## 1. Layout

```text
+--------------------------------------------------------------------------+
| Status bar: AIS feed LIVE 12:04:18 UTC (2 s)  | 287/300 reporting | 6 stale |
+--------+-----------------------------------------------+-----------------+
| Filter | [search: name/MMSI/call sign]          [+][-] | ALERTS (7)      |
| chips  |                                               |  ! Collision  2m|
| Type   |                  MAP                          |  ! Geofence   5m|
| Status |      (dark muted harbour chart)               |  ~ Stale ping 9m|
| Zone   |                                               | ----------------|
|        |                                               | VESSELS (300)   |
| 120 of |                                               | name  st  age   |
| 300    |  [legend]                       [layers][N]   | row row row ... |
+--------+-----------------------------------------------+-----------------+
| HISTORY: [|<] [play] [>|] 1x  ----o-----------|  -2h ... now  [events] [LIVE]|
+--------------------------------------------------------------------------+
| attribution (always visible)                                             |
+--------------------------------------------------------------------------+
```

- **Top status bar** (freshness, D02): feed state, last update time in UTC with seconds, count of vessels reporting versus stale or lost. Text plus icon, never colour alone. The message "live" turns into "STALE 02:10, last data 12:02:08" when the feed itself stops. This is the most important line on the screen, because a frozen map looks the same as a quiet harbour.
- **Map** takes the most space. Zoom and search stay in their standard corners, and the layers control and legend do too. The search box is always visible (I16). Attribution is visible on load (C01).
- **Right column**: alerts on top, vessel list below. They share one selection state with the map (I05, D09). Clicking an alert or a row zooms to the vessel and highlights it. Selecting on the map scrolls the list to that row. The list has a text and table equivalent of the map (A01).
- **Left filter chips** (type, status, zone, operator). Always show "N of 300 shown" and a clear-all action (I09). Filters never hide an alerting vessel without telling the dispatcher: alerting vessels stay visible and the chip row shows "+2 alerting outside filter".
- **Bottom history dock**: collapsed to a thin strip in live mode and expanded in replay mode. See section 4.
- **Selected vessel**: a detail drawer replaces the lower half of the right column. It shows name, MMSI, type, status, speed and heading, destination, last fix time, and action buttons (contact, assign, replay this vessel). It holds no personal data of crew (I11).
- **Keyboard** (A02, A03): a skip link before the map, tab order of status bar, filters, list, alerts, history. Map-only actions all have a list or keyboard equivalent. Markers or their list rows have accessible names (A08), for example "Tug Aurora, moving 6 knots, last fix 4 s ago".

## 2. Symbology

Rule: **type by shape, state by fill and badge, age by fade and ring, selection by a second colour.** Never one channel for two things.

| Channel | Encodes | Details |
|---|---|---|
| Shape | Vessel class | Heading-rotated triangle or hull for cargo/tanker/passenger, a distinct outline for tug/pilot/service boat, a diamond for fixed aids or unmanned units, a small circle with no arrow when speed is under about 0.5 kn (no reliable heading, so no arrow). Shape must still tell classes apart in grayscale. |
| Fill colour | Operational status (moving, at anchor or moored, working/assigned, alert) | Use the 5-level severity palette and the CARTO Safe palette from the knowledge base (CVD-safe); do not invent hexes. Alert state also gets a badge (!) and a thicker outline. |
| Opacity and ring | Data age | See section 3. |
| Selection | Selected vessel | A second colour halo (not any status hue) plus the full track of that vessel only. |
| Label | Name | Only at zoom levels where it fits, only for selected, alerting, and service boats you own. Halo on labels so they stay readable on the dark basemap (S20). |

Palette values taken from the matched blueprints:
- Vessel type / qualitative (maritime): #148EBF, #B74C1B, #148045, #8148DA, #B5810A, #8C8C8C (synth)
- Severity (5 levels): #5581AE, #127A74, #B67A03, #B64F10, #E835A2 (synth)
- CARTO Safe 7 (+grey other): #88CCEE, #CC6677, #DDCC77, #117733, #332288, #AA4499, #44AA99, #888888 (sourced)
- Use one palette for type or status, not both on the same channel. Suggested split: status uses the severity palette. Type is carried by shape, with colour only a secondary cue, so the map never becomes a rainbow.
- Signature accent for your own fleet (service boats): one colour that is not in any of these ramps (S19).

Other symbology points:
- Layers on by default: live vessels, geofences and zones (outlines, such as channels, anchorages, restricted areas, berths), alert markers. Off by default: selected-vessel planned route, density/heat trace, AIS coverage footprint, weather.
- **Track trails**: short fading trail (last 5 to 10 min) on all vessels in a dim tone, a full trail only for the selected vessel. Never draw all history at once.
- **Clustering**: with 300 objects spread over a harbour, do not cluster by default. At the lowest zoom (whole region) cluster with a count, and set a max zoom so they split before the harbour view (S16). In berth areas where boats overlap, use a fan-out on click, not an automatic spiderfy.
- **Legend**: always on and collapsible, tied to the visible layers, with the age encoding shown in it. Do not hide it behind the layers panel.
- **Basemap**: dark muted marine chart with few labels (Signal Track tone), designed rather than inverted. Keep depth contours and navigation marks faint but present. Land is a flat tone, water is a slightly lighter tone, so the vessel glyphs are the brightest thing on screen.

## 3. Data age and status: what the dispatcher sees

Three separate things must not be mixed: **vessel status** (what it is doing), **data age** (how old the position is), and **feed health** (whether the system itself is receiving data).

**Per vessel (age of last fix), recommended default thresholds (synth, tune per feed, as reporting rates vary by class and speed):**

| Age | Look | Meaning |
|---|---|---|
| Fresh (under 2 min or within 2x the expected report interval) | Full opacity, solid glyph | Position is current |
| Ageing (2 to 10 min) | 60% opacity, age text appears in list ("4 min") | Position is an estimate |
| Stale (10 to 30 min) | 35% opacity, dashed outline, small clock badge, a dead-reckoning "last known" ghost, no arrow animation | Do not rely on it for decisions |
| Lost (over 30 min) | Hollow glyph at last known position with a ring that grows with time, listed in a "Lost contact" group, raises a warning alert | Search area, not a position |

- Age appears as text everywhere a vessel is shown: list column "Last fix", hover tooltip, detail drawer ("12:01:55 UTC, 3 min 12 s ago"). The row sorts by age on demand.
- Do not smoothly animate a vessel across a long gap. Interpolate only between fixes (150 ms motion), and extrapolate (dead reckoning) at most briefly, drawn as a different style (dashed) so it is never confused with a measured position.
- Where a vessel reports less often by design (anchored, moored), the thresholds scale by status, so a moored boat is not flagged as stale after 3 minutes. State the rule in the vessel drawer ("expected every 3 min while moored").
- **Source and quality**: show the source per vessel (AIS, radar, own GPS tracker), and mark low-quality fixes (jump, implausible speed) with a small flag instead of silently moving the vessel.
- **Feed health bar** (top): per source "as of" time, latency, and health (freshness and status bar widget; states loading, error, stale). If a feed goes down, the map shows a banner and dims the whole vessel layer for that source, so 40 boats do not each look individually "stale".
- **Coverage gaps**: show where the receiver has no coverage (optional layer) so a missing vessel is not read as a vessel that is not there.
- KPI tiles (few, with units and a reference, D01): Reporting 287/300 (vs 296 an hour ago), Alerts open 7, Stale or lost 6, Average fix age 8 s. No more than four.

## 4. History and replay

Principle: history is a **mode**, not a separate screen, and it must never be confused with live.

- **Entering**: three ways. (1) Click "History" on the bottom dock. (2) "Replay this vessel" in the vessel drawer. (3) "Replay around this alert" on an alert, which opens the window from 15 min before to 15 min after the event, centered on its location.
- **Mode must be unmistakable**: in replay the whole frame changes: a persistent banner "REPLAY - 11 Nov 2026 09:14:30 UTC" (date and time in UTC, with a local-time option), the status bar live indicator turns to "not live", the map gets a thin accent border, and the alert list switches to events in the replay window. A "Return to LIVE" button is always visible. Live data keeps arriving in the background, with a small badge "3 new alerts since replay start".
- **Scrubber (hero element, Signal Track)**: a docked time bar with window presets (last 1 h, 6 h, 24 h, custom), play/pause, step back and forward by fix or by minute, speed (1x, 4x, 16x, 60x), loop off by default, and a draggable playhead. Event ticks on the bar mark alerts, geofence entries and exits, and stops. Dragging the playhead jumps; the map updates after release, or in real time if the data is cached.
- **Scope selection** so there is not too much on screen: replay all vessels (shows positions and short trails only) or the selected vessel(s) (full track). Cap at a few vessels with full tracks (for example 5) and say so. Pin-to-compare lets a dispatcher put two vessels on the same time base, which answers close-approach questions.
- **Playback behaviour** (T04): pause automatically while data is loading and never skip frames silently; show a loading state in the scrubber. Show the actual data as it was received, with the same age fade, so a replay shows what the dispatcher would have seen, and an optional toggle shows "reconstructed" (interpolated) positions in another style.
- **Track presentation**: line coloured by speed or by a single tone, with arrow ticks for direction, dots at actual fixes (toggle), stops marked with a duration label. Hover on a track shows time and speed at that point, and click pins it.
- **Export and share**: copy a permalink to a time and vessel, export the track as CSV or GPX, and "add to incident note". Time ranges and filter state are in the URL.
- **Time**: all stored and displayed in UTC with the local offset visible (I mean "12:04 UTC (14:04 local)"), never ambiguous at day boundaries.
- **Reduced motion** (A13): playback uses stepwise jumps, no flying camera (jumpTo instead of flyTo), no animated trails, and a pause control for any continuous motion. The scrubber stays fully usable by keyboard (arrow keys step, space plays, Home/End jump to start and now).

## 5. Alerts

- Severity model: **critical** (collision risk, grounding risk, man overboard, SOS, entry to a restricted zone), **warning** (geofence breach, speeding in channel, drifting at anchor, loss of contact, late arrival), **info** (arrivals, departures, berth changes). Safety rules critical, operational rules warning (fleet-tracking guidance).
- Each alert row: severity icon plus word, short title, vessel name, location or zone, time and age, state (new, acknowledged, assigned, resolved). Status workflow, not just a log. Sorted by severity then time (D09). Never encode severity by colour only (A07).
- Clicking an alert zooms to the vessel, highlights it, and offers "Replay around this" and "Assign". Acknowledging is one click and keeps the item visible but quieter.
- **Alert fatigue controls**: de-duplicate (one alert per condition per vessel, with a count), a cool-down so a vessel hovering at a boundary does not re-fire, grouping ("5 vessels in anchorage B left the zone"), and a rule that only critical alerts use sound, with a mute and a visible muted state. Show a ceiling: "7 open, 2 critical".
- A critical alert uses a short pulse on the map marker. The pulse stops after acknowledgement and does not loop under reduced motion; a static ring replaces it.
- Stale data alerts are separate from safety alerts, so a feed problem does not bury a collision warning.
- A safe wording note: an alert says what was observed ("no report for 12 min"), not an assumed cause. The pitfall from the maritime playbook applies: a gap can be technical, not an incident.

## 6. Interactions
- Hover highlights only (feature state and cursor); click opens the drawer (I02).
- Search by name, MMSI, call sign and berth. Results list stays visible and the map flies there (jump with reduced motion).
- Multi-select by box draw for a group action (assign nearest boat, broadcast message).
- Measure distance and bearing, plus a "nearest service boat to here" helper for dispatch; the result is a list ordered by ETA, not a hidden calculation. State the assumption (straight line or routed).
- Draw or edit geofences with undo; changes are logged.
- Popups carry no personal data of crew or owners (I11).

## 7. Signature (balanced, ops room)

- **A. Signal Track (recommended)**: dark muted marine basemap, compact 6 px cards, heading-rotated icons by type, fading trails, replay scrubber as the hero, Inter for UI and JetBrains Mono for IDs and times. It fits because replay answers the dispatcher's question "what happened here".
- **B. Night Ops**: lower glare for 12-hour shifts, hero is a freshness strip with a live/stale pulse. Choose it if the dispatcher mostly watches live and replay is rare.
- **Baseline: Civic Paper with signature removed**: plain light basemap, default markers, solid panels, no hero. It still has the same layout, same data and same conventions, so it ships if the signature is cut. It is also the right choice for a bright control room.
- Locked: control positions, click and drag conventions, shape before colour, selection in a second colour, attribution, CVD-safe palettes. Signature never recolours data (S19) and the accent is not in any data ramp.
- Motion: 150 ms, positions interpolated between fixes, reduced motion jumps to the latest position and drops trail animation.

```text
A  Signal Track                      B  Night Ops                     Baseline: Civic Paper, no signature
+------------------------------+     +------------------------+       light basemap, default markers,
| dark chart, arrows, trails   |     | very dark, dim chrome  |       same layout, no hero.
|  > > ^   o  (aging ghosts)   |     |  live strip pulsing    |
| |>  ---o------------- LIVE|  |     | [LIVE 12:04:18  2s]    |
+------------------------------+     +------------------------+
```

Test plan: 5-second test (can a dispatcher say how many vessels are in alert and whether the feed is live?), first-click test ("find the tug nearest berth 4"), squint test (are alerting and stale vessels still distinguishable when blurred?), and preference test of Signal Track against the baseline.

## 8. What to avoid
1. **Stale positions shown as current.** Fade, badge and age text are mandatory. A frozen feed must be loudly visible.
2. **Colour-only meaning** for status, severity or age (A07). Pair with shape, badge, text.
3. **A rainbow of types.** Use shape for type, a few colours for status.
4. **Drawing all trails or all history at once.** Short trails for all, full track for the selected only.
5. **Animating through gaps** as if the vessel really moved smoothly; mark estimates differently from measurements.
6. **Replay that looks like live.** Always show a banner, a different frame and a return-to-LIVE button.
7. **Alert fatigue**: no duplicate or flapping alerts, no sound for non-critical, no alert that cannot be acknowledged.
8. **Mixing feed outage with vessel problems.** One banner for the feed, not 40 stale boats.
9. **Hiding vessels with filters silently.** Show "N of M" and keep alerting vessels visible.
10. **Moving standard controls or hiding the search box and legend**, or making the signature recolour data.
11. **Clustering at working zoom, or DOM markers** for hundreds of items; use a map layer for the glyphs. 300 objects are cheap, so the cost is design, not performance.
12. **Overlapping labels.** Label only selected, alerting and own boats; never all 300.
13. **Ambiguous time.** Always UTC with a local offset, and the date on the replay bar.
14. **Assuming a cause**: "no report" is not "incident".
15. **Attribution or basemap credits left out** (C01) and low-contrast labels on the dark basemap (text 4.5:1, graphics 3:1).

## 9. Self-check against the skill
- Locked conventions unchanged: pass. Data ramps taken from the palettes, accent outside them: pass (accent hue to be picked outside the listed hexes and verified).
- Reduced-motion path: specified for replay, trails and the alert pulse.
- Contrast on the dark basemap: **not yet measured**; must be checked on the real basemap (text 4.5:1, graphics 3:1, halos visible).
- Signature removable: yes, via the Civic Paper baseline.
- Not met or open: age thresholds and report intervals depend on your real feeds; zone and alert rule lists depend on your harbour authority; no mock was built, since none was requested.
- Checklist items covered: S16, P03, D01, D02, D09, I02, I05, I09, A01, A02, A03, A07, A08, A13, C01, T04, S09.
