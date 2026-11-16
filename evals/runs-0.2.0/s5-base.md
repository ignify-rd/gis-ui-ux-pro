# Design Brief: Harbour Dispatcher Operations Screen

## Assumptions
- One dispatcher, one large desktop monitor (1920x1080 or wider), optionally a second screen. Used for long shifts, possibly in a dim control room, so a dark theme is the default with a day theme available.
- About 300 vessels and service boats. Position reports come from AIS or GPS and arrive every few seconds to several minutes, depending on vessel class and receiver coverage. Reports are not guaranteed to be regular.
- The dispatcher's core tasks are: (1) know what is happening now, (2) notice what needs action, (3) find a specific vessel fast, (4) reconstruct what happened.
- Alerts come from rules such as geofence entry, speed, collision proximity, a vessel stopped in a channel, and signal loss. Rule definitions are out of scope.

## 1. Layout
Three regions around a map. The map is the primary surface and takes about 60 to 65 percent of the width.

- **Top bar (slim).** Shows the live/replay mode indicator, the clock (local time, UTC on hover), feed health ("Feed OK, last message 2 s ago"), the alert counts by severity, and global search. Search takes a name, MMSI, call sign, or fleet ID.
- **Left panel, vessel list (about 22 percent).** Sortable, filterable table. Columns: status dot, name, type icon, speed, last-seen age, and alert badge. Filters are chips: All, Alerting, Stale, My fleet (service boats), Cargo, Passenger, and so on. The default sort is "needs attention" (alerting first, then stale, then the rest by name). Selecting a row selects the vessel on the map, and the reverse also works. Hovering a row highlights the vessel on the map.
- **Centre, map.** A nautical-style basemap that is muted and low-contrast so vessels stand out. It shows harbour features: channels, berths, anchorages, restricted zones, and the key geofences, all drawn faintly. Controls are zoom, a "fit to all" button, a layer toggle, and a scale bar.
- **Right panel (about 18 percent), context.** It has two tabs: Alerts and Selected vessel. The Alerts feed is the default. An alert click flies the map to the vessel and opens its detail. The Selected vessel tab shows identity, position, speed, course, destination, data age, status, recent alerts, and a "Show history" button.
- **Bottom timeline (collapsed by default).** It opens when the dispatcher enters history mode (section 4).

The dispatcher should never need more than one click to get from an alert to the vessel and its context.

## 2. Vessel symbology
At 300 vessels, individual symbols are feasible, so don't cluster at harbour zoom levels.

- **Shape.** A small chevron or ship-shaped marker rotated to course over ground. Vessels with no speed (moored or anchored) are drawn as a circle, with no heading arrow. This tells moving and stationary apart at a glance.
- **Colour encodes class, not severity.** A muted palette of about 4 hues: service boats (own fleet), cargo/tanker, passenger, and other. Colour is not used for alert state, so the alert colours stay unambiguous.
- **Alert state is a separate channel.** An alerting vessel gets a ring or halo in the severity colour (amber for warning, red for critical) and a larger marker. The halo shape also differs by severity (dashed versus solid), so it doesn't rely on colour alone.
- **Selected vessel.** A bright outline, its label always on, and a short track tail (last 10 to 15 minutes).
- **Labels.** Names are shown only for selected, alerting, and hovered vessels, plus all vessels at the closest zoom level. Show them with collision avoidance, never overlapping.
- **Speed vector.** An optional line projecting where the vessel will be in N minutes, toggled on. It helps with closing-situation judgement.
- **Zoomed out beyond the harbour.** Switch to simple dots and cluster only at that scale, with the cluster badge showing the highest alert severity inside.
- **Accessibility.** Don't depend on red/green alone. Use shape, dash pattern, and an icon in addition to colour. Text on the dark theme meets 4.5:1 contrast.

## 3. Data age and status
This is the most important trust signal. A dispatcher must never mistake an old position for a live one.

**Age is shown continuously, not only on demand.**
- Every vessel has a "last seen" age computed on the client from the report timestamp (not the receive time), and it ticks up on its own, even if no new data arrives.
- Age tiers, tuned per vessel class because reporting rates differ (a fast ferry reports more often than an anchored barge):
  - Fresh: within the expected interval. Full-opacity marker.
  - Late: more than about 2 expected intervals. Marker is slightly faded, and the list shows the age in amber text.
  - Stale: more than about 5 expected intervals, or more than N minutes. Marker is hollow or dashed-outline and clearly dimmed, and the list shows "Stale 12 min".
  - Lost: beyond a lost threshold (for example 30 minutes) or flagged by the rule engine. The marker becomes a "last known position" symbol with a dotted line to a ghosted heading, and a signal-lost alert is raised.
- A stale vessel is never drawn at its dead-reckoned position as if it were live. If a projection is shown, label it explicitly as an estimate.
- The age appears on the marker tooltip, in the list, and in the detail panel, always in the same format ("42 s", "6 min", "2 h 10 min").

**Status is a short, fixed vocabulary** shown as text plus icon: Underway, Anchored, Moored, Not under command, Service (on task), Offline/Lost. Source: the report's navigational status where present, otherwise derived from speed and position, with the derivation labelled as "inferred".

**Feed health is global.** The top bar shows the feed state. If the entire feed stalls (no messages from any vessel for more than about 30 s), show a prominent banner, "Live data interrupted, positions as of hh:mm:ss", and desaturate the map. Otherwise every vessel would look stale one by one, and the real problem would be missed. Reconnection shows a brief "Feed restored" notice.

**Provenance.** The detail panel shows the source (AIS terrestrial, satellite, GPS tracker) and the timestamp, because source quality affects how far to trust a position.

## 4. Alerts
- The Alerts tab lists active alerts, newest and most severe first, grouped by vessel when one vessel has several. Each item has severity, rule name, vessel, time raised, and time since.
- States: New, Acknowledged, Resolved. The dispatcher can acknowledge with one click or a key. Acknowledged alerts keep their halo but at a quieter style. Resolved ones leave the active list and remain in the history.
- Sound is reserved for critical alerts only, with a mute-for-N-minutes option. Everything else is silent and visual.
- A new alert briefly pulses its marker once, not continuously. Continuous animation across a screen of 300 objects causes fatigue and hides the real signal.
- Alert fatigue control: de-duplicate repeats of the same rule on the same vessel, and use a hysteresis or minimum re-alert interval.
- An alert click centres the map without changing the zoom unnecessarily and does not clear the dispatcher's own filters.

## 5. History and replay
History is a mode, clearly separated from live. The dispatcher can never confuse the two.

- **Entering.** From a vessel's "Show history", from an alert ("Replay around this alert"), or from the mode switch in the top bar.
- **Mode signalling.** In replay the top bar turns a distinct colour with the label "REPLAY, 14 Nov 09:12:30", the map frame gets a coloured border, and the live alert sound is suppressed. A single "Return to live" button is always visible.
- **Timeline.** A scrubber along the bottom with the selected window (default: last 1 hour, presets of 15 min, 1 h, 6 h, 24 h, and custom range). Alert events appear as ticks on the timeline. Gaps in data are shown as hatched segments, so missing data is visible rather than hidden.
- **Controls.** Play/pause, speed (1x, 10x, 60x, 300x), step to the previous/next event, and a draggable playhead. The keyboard works: space for play, arrows for stepping.
- **Scope.** Two views:
  - *Single vessel track:* the full path drawn as a line, with the colour fading from old to new and position dots at actual report times (not interpolated points, so the data's real sampling is honest). Hover a dot for time, speed, and course.
  - *Whole-harbour replay:* all vessels move as at the time, with short trails. Between reports, positions are interpolated for smooth movement but are marked as interpolated (for example, a subtle style), and vessels with a gap longer than the stale threshold at that moment are drawn stale, using the same rules as live.
- **Alerts in replay.** The alerts that were active at the playhead's time are shown in the right panel, so the dispatcher sees what the situation looked like then.
- **Comparing.** Allow pinning a vessel or two so their tracks stay highlighted while the rest dims.
- **Export.** Export the selected window as a report (CSV of reports and alerts, plus a map image) for incident reviews.
- **Performance expectations.** Loading a 24 h window for 300 vessels must show something within a couple of seconds, so load the single-vessel track first and the rest progressively, with a visible progress state.

## 6. Interaction and performance
- Everything the dispatcher does often is reachable by keyboard: focus search (/), next alert (N), acknowledge (A), toggle history (H), return to live (L), fit all (F).
- Updating markers must not make the map jump. Never re-centre or re-zoom automatically on position updates. Provide an optional "follow selected vessel" toggle, off by default.
- Smooth, brief marker movement between reports (under 1 s). No animation that implies a certainty the data does not have.
- Target: 300 markers updating with a steady 60 fps pan and zoom on ordinary control-room hardware. Use a GPU-rendered layer rather than DOM markers.
- Layout state (filters, layers, panel sizes) persists across sessions and reloads.
- Empty and error states are designed: no vessels match the filter, no history in the window, history service unavailable.
- Time is always shown with its zone, and the same zone is used everywhere.

## 7. What to avoid
- Showing stale positions as live. This is the worst failure for this screen. Age must always be visible and tick without new data.
- Using colour as the only signal, or using the same colour for class and for severity.
- Clustering at harbour zoom levels, which hides the very vessels the dispatcher must watch.
- Labels on all vessels at all zoom levels. They turn into clutter.
- Continuous pulsing, blinking, or bouncing for many items. Pulse once on new alerts only.
- Modal dialogs that cover the map during live operation. Use side panels and non-blocking toasts.
- Replay that looks like live. A mode that is easy to miss is a safety risk.
- Interpolating through data gaps without marking it, and drawing smooth lines across lost periods.
- A busy basemap, or default web-map styling with bright roads and land, which fights the vessel symbols.
- Auto-recentring and auto-zooming on updates or alert arrival while the dispatcher is working somewhere else.
- A flood of low-value alerts. Too many alerts make the critical ones get ignored.
- Hiding the list on smaller screens. The list and alerts are core, so collapse the right panel before the list.
- Dashboards of charts and KPIs that compete for space with the map. Add aggregate counts only as small badges in the top bar.

## 8. Open questions for the team
- The actual reporting intervals per vessel class, to set age thresholds.
- Whether the dispatcher can act on a vessel from this screen (call, message, assign a task) or only observe.
- How long history is retained, and how large a window the history service can serve.
- Whether several dispatchers share alert acknowledgements.
