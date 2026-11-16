Problem:   service-requests (runner-up data-catalog) - residents viewing and following reported city issues
Layout:    list-first locator, map toggle on phones, detail as bottom sheet
Direction: Civic Paper, subtle (alt Canvas Studio; baseline Civic Paper with signature removed)
Hero:      sentence legend "Each marker = one report, last 30 days"
Risks:     status by colour only (A07) - PII in popups (I11) - stale data without a timestamp (D02) - HTML injection from free text (I10) - small touch targets for older users

# Design brief: public issue-tracking map

## Assumptions (nobody to ask)
- Audience: the general public, many older and on phones, often outdoors in sun, on slow mobile data. Anonymous browsing, no login to view.
- Feeling: calm, trustworthy, plain-spoken. A council service, not a tech dashboard.
- No brand system was given. The council's own colours and fonts can replace the tokens below, but they must not collide with the data colours.
- Intensity is subtle. This is a civic product and the skill defaults to quiet. It is a synth-level default and you can override it.
- Statuses are four: Reported, Acknowledged or scheduled, In progress, Fixed. Rename them to match the council's real workflow.
- Basemap is a free or open tile service, and its attribution is shown.

## Two directions plus the baseline

```text
A  Civic Paper (subtle) - RECOMMENDED      B  Canvas Studio (subtle)        Baseline
+------------------------------+           +------------------------------+  Civic Paper, signature
| [ Search address or street ] |           | [search] [tools]       [+][-]|  removed: plain light
| [Pothole][Light][Drain] [All]|           |  soft strokes, friendly      |  basemap, solid panels,
| 42 of 310 shown  [Clear all] |           |  note-like callouts          |  default markers, no hero.
|------------------------------|           |                              |  Same layout and data.
| (list) Pothole, Oak St       |           | [Map] [List]        [legend] |  Ships if the signature
|  (map) Light out, 5th Ave    |           +------------------------------+  is cut.
|  light-gray map, shapes      |
| "Each marker = one report,   |
|  last 30 days"      [+][-]   |
+------------------------------+
```

**A. Civic Paper.** Mood: a clean municipal paper map. The user first sees a light, quiet basemap with a big search box and category chips. Hero: the sentence legend ("Each marker = one report, last 30 days"). It tells a first-time resident how to read the map without a key. Variation for this product: airy density (larger spacing and touch targets), neutral temperature, 12px radius, instant tempo.

**B. Canvas Studio.** Mood: friendly and collaborative. Soft strokes and note-style callouts. It suits a participatory "neighbourhood workshop" tone, but it is warmer and less sober for a service that reports on faults.

**Recommendation: A.** It matches the audience (older, trust-seeking) and its hero explains the map in one sentence.

## Look and feel (tokens, Civic Paper)
| Token | Value |
|---|---|
| Basemap | Light gray or white, sparse labels, muted roads. Reference: CARTO Positron, Protomaps white or Esri Light Gray Canvas. Street names stay readable, because residents locate themselves by street. |
| Surface | Solid white panels, 12px radius, 1px border, no blur or glass, no shadow |
| Motion | 110-150 ms, productive easing. Reduced motion: jumpTo instead of flyTo, no transitions (A13). |
| Type | Public Sans (UI) + Source Serif 4 (titles). Body at least 16px, labels at least 14px. Allow text zoom to 200% without breaking layout. |
| Accent | One civic accent for controls and selection only. It must not reuse any data hue. The status palette already uses a blue (#5581AE), so make the accent a dark navy or ink, clearly different from that blue. |
| Contrast | Text 4.5:1 and graphics 3:1 against the actual basemap, not just the panel. Check marker outlines against the gray basemap in direct sun. |

## How requests are drawn
Each request is a marker. The marker has a shape, a category icon and a status colour, so the meaning never rests on colour alone (A07, critical).

- **Status = colour plus a status mark inside the marker.** Colours come from the generic 5-level qualitative palette in the knowledge base (synth, CVD-considered): Reported #5581AE, Acknowledged #127A74, In progress #B67A03, Fixed #B64F10. The fifth hue, #E835A2, is held back for overdue. Do not invent other hexes. Because that blue and brown can look close for some users, rely on the status mark (empty circle, half-filled, filled with spanner, tick) and keep the status word in the list and the sheet. Check the final set in a colour-blindness simulator (S09) and swap to a sequential palette if it fails.
- **Category = icon** (pothole, lamp, drain), large and simple. One icon family only.
- **Overdue = extra outline or a "late" badge, not a hue change.** The skill's pitfall is a colour-only overdue flag. Wording on the public map should be neutral, for example "Past target date".
- **Fixed requests** are off by default (open requests only), with a filter "Show fixed in last 30 days". This keeps the map readable and honest about what is open.
- **Clusters** at low zoom show a count. Tapping a cluster zooms in. Cluster text stays at least 16px.
- **Selected marker** gets a ring and enlarges. It is the single selection style.
- **Size:** markers have a minimum 44x44 px tap area even when the drawn dot is smaller.
- **Neighbourhood boundaries** are on, as thin gray outlines. An optional "reports per 1,000 residents" or per-area heat view is off by default. Any area shading must use rates, not raw counts (S01, critical), and is a secondary view.

### Layers
| Layer | Default | Symbology |
|---|---|---|
| Open requests | On | Category icon, status colour plus status mark, clustered at low zoom |
| Neighbourhood boundaries | On | Thin gray outline |
| Fixed requests (30 days) | Off | Muted, check-mark marker |
| Volume heatmap or rate | Off | Normalised rate, sequential ramp (YlOrRd 5-class, sourced: #ffffb2 #fecc5c #fd8d3c #f03b20 #bd0026) |

Reuse of hues: YlOrRd overlaps the status browns and oranges, so show it only when the request layer is hidden or faded, and never both at full strength.

## Layout and mobile
- **List-first locator.** Search and filters on top, results list on the left, map on the right on desktop. On phones the list comes first and a clear "Map" toggle swaps the view. The skill describes this as the default pattern for 311 maps.
- **Mobile:** bottom sheet with three heights (peek, half, full). Marker tap opens the sheet at half height. The map stays visible above it.
- **Controls stay in the platform corners:** zoom and search where users expect them, attribution visible on load (C01, critical). Add a "Find my location" button and a visible address search. Do not rely on pinch-only or hidden gestures. Plus and minus buttons stay.
- **Filter chips:** Category, Status, Neighbourhood, Date. Show "42 of 310 shown" and a "Clear all" (I09). Chips are large and labelled in words.
- **Map and list stay in sync.** Selecting in one highlights in the other. The list is the equivalent of the map (A01) and gives keyboard and screen-reader users the full content.

## What a click shows (detail sheet)
Title first, then curated fields only (I04), rendered as plain text, never as raw HTML (I10).

1. **Title:** "Pothole, Oak Street near No. 24" (street-level location, not a house number if that could identify a reporter).
2. **Status line:** icon, word and colour, plus "Past target date" if applicable.
3. **Status timeline:** Reported (date) - Acknowledged - In progress - Fixed. Show dates with a zone label, for example "12 Nov 2026, 14:05 local time". Store and query in UTC (T10).
4. **Expected fix:** "Target: 20 Nov" or "Not yet scheduled". Answers the residents' key question "when will it be fixed?"
5. **Photo** (reviewed, with alt text), if the council allows it.
6. **Plain-language summary:** what the council will do, and which team handles it (a team, not a named person).
7. **Actions (large buttons):** "Follow this request" (email or SMS alert, optional), "Report a duplicate nearby", "Share link".
8. **Footer:** "Last updated 14:05 today" (D02), plus the request reference number.

States: loading skeleton, "We could not load this request. Try again", empty ("No reports match your filters. Clear filters"), stale ("Data last updated 3 hours ago").

Behaviour: hover on desktop shows only a short tooltip. Click or tap opens the sheet (I-rule on hover vs click). Escape or a visible "Close" button dismisses it. Deep links (`/request/12345`) open the same sheet, so people can follow a request from an email.

## Following status
- A reference number and a shareable link per request.
- Optional "Follow" alerts (contact details are held by the council backend and never shown on the map).
- A "My follows" list, stored locally or with an account, if wanted. Keep it optional so anonymous browsing still works.
- "What's new" feed: recent status changes near me, limited to 30 days.
- Summary tiles (few, with reference value and units, D01): "Open near you: 12", "Fixed this month: 38 (up from 31 last month)", "Median days to fix: 6 (target 10)". Each with a last-updated stamp.

## Temporal
- Default window: rolling 30 days.
- Filters: Reported date and Fixed date as simple presets (Last 7 days, Last 30 days, This year) plus a custom range. No timeline slider is needed. If one is added, give it plus and minus buttons and a text equivalent.
- Show age as words: "Reported 5 days ago".

## Care points (must-do list)
1. **Privacy (I11, high).** Never show reporter names, phone numbers, emails or exact home addresses. Publish only a street-level location or snap points to the road segment or a block midpoint. Omit those fields from the public query itself, not only in the UI. Photos can capture faces and number plates, so moderate or blur them. Free-text descriptions can include names. Review or strip them before display.
2. **Safe rendering (I10).** Treat all report text and photos as untrusted. Insert as text only. No raw HTML from data.
3. **Not colour-only (A07, critical).** Status, category and overdue all have a non-colour cue. Test in greyscale and with a colour-blindness simulator.
4. **Older users and phones.** 44 px minimum targets, 16px+ body text, high contrast, plain words ("Fixed", not "Closed - resolved"), no hidden gestures, no hover-only content, no auto-moving map, a visible "Back to list". Keep the one-column phone layout simple. Test with real older residents.
5. **Keyboard and screen reader (A01-A03).** A text summary and list that mirrors the map, tab order that can leave the map, a skip link before it, visible focus. Sheet focus moves into the sheet and returns to the marker on close.
6. **Reduced motion (A13).** jumpTo instead of flyTo, crossfade for the sheet, no looping animation, no pulsing markers.
7. **Freshness and honesty (D02).** Show "Last updated" on the map and in the sheet. If the feed fails, say so and show the last known data marked as stale instead of an empty map. Public reports are not a count of all problems, only of reported ones, so state that, and do not use raw counts to compare areas (S01). Show rates, or avoid the comparison.
8. **Duplicates.** Merge or link duplicate reports so demand is not double counted. "Report a duplicate nearby" adds a "+1 me too" to the existing request rather than a new marker.
9. **Overdue wording.** Public "Past target date" can create anger. Keep the tone neutral and always show the next step.
10. **Locations and errors.** Geolocation is opt-in with a clear reason, and the app works without it. Handle low accuracy ("Location approximate").
11. **Attribution (C01, critical).** Visible on load. If the tile provider is Leaflet or OpenLayers based, add the provider credit explicitly (C03).
12. **Performance on phones (P-rules).** Vector tiles or slim GeoJSON, cluster server-side or client-side, loading and error states, and no heavy map libraries blocking the list. The list shows first, so the page is useful even before tiles load.
13. **Time (T10).** Store UTC, display local with a zone label. Convert the start and end of the chosen date range to UTC before querying.
14. **Language and translation.** Public councils usually need multiple languages and right-to-left support. Make the legend sentence and labels translatable.

## Signature and locked conventions
- Locked: control corners, click opens details, drag pans, pinch zooms, standard icons, attribution, data colours from the listed palettes only.
- Signature zones (vary per product): basemap tone, panel shape, type pair, one accent, marker style, motion, the sentence legend.
- Hard rule (S19): the signature never recolours data or moves controls. Removing it leaves a fully usable app, which is the baseline.

## Test plan
- **5-second test:** can a resident say what the map shows and what the colours and shapes mean?
- **Preference:** baseline versus Civic Paper, with older participants.
- **First-click:** "Find the pothole near your street", "Find out when it will be fixed".
- **Squint and sun test:** look at the phone outdoors or at low brightness. Statuses should still be distinguishable by shape.
- **Greyscale and colour-blindness check** of the status markers.

## Pre-delivery checklist (rule ids)
- [ ] No personal fields in the query, popups or exports (I11)
- [ ] Every colour meaning also has an icon, shape or label (A07)
- [ ] Palette checked for colour blindness (S09)
- [ ] Any area shading is a rate, not a count (S01)
- [ ] "Last updated" shown and aligned with the layer (D02)
- [ ] Curated popup, title first (I04); text only, no raw HTML (I10)
- [ ] Filter chips with "N of M shown" and clear-all (I09)
- [ ] Times stored in UTC, shown with a zone label (T10)
- [ ] KPIs have units and a reference value (D01)
- [ ] Attribution visible on load (C01, C03)
- [ ] Text summary and list equivalent (A01), keyboard operation (A02), skip link (A03)
- [ ] Reduced-motion path specified (A13)
- [ ] Signature removable, baseline works with the same layout and data

## Evidence note
The layout, layers, pitfalls and rule list come from the service-requests playbook, which is labelled synth (a reasoned default, not a single-source fact). Rules A07 and S01 are marked critical in the knowledge base. Specific numbers I added (44 px targets, 16 px text, 30-day window, four statuses) are my recommended defaults, not sourced requirements. The two status-palette concerns (blue accent clash, blue and brown similarity) should be verified with a colour-blindness simulation on the final basemap.
