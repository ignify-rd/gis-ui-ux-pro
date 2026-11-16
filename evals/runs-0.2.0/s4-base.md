# Design Brief: Public Problem-Report Map

Assumptions: mobile-first (most users on mid-range phones, some on slow data), many users 60+, the council already has a request system with an API (id, category, status, location, dates, optional photo). Residents view and follow; reporting is a separate flow and is out of scope here. Public site, so it must meet WCAG 2.2 AA, and I recommend AAA for text contrast.

## 1. Look and feel
- Tone: calm, civic, trustworthy, plain. It should feel like a council service, not a tech demo. Light theme, white and pale-grey surfaces, one council brand colour for chrome only (not for data).
- Basemap: muted, low-contrast greyscale or soft streets with clear road and place names. Data must stand out against it. Label sizes are large enough to read; no decorative labels.
- Type: system sans-serif or one highly legible face. Body 18px minimum, map-card titles 20px, line height 1.5. Users can scale text to 200% without breaking layout. Plain language, with no jargon such as "ticket", "SLA" or "triage".
- Touch: every control is at least 48x48 px with 8px spacing. Buttons carry text labels, not icon-only (for example "Search address", "My location", "Filter"). Avoid hover-only behaviour, gestures that need two fingers as the only option, and tiny close buttons.
- Layout on phone: full-screen map, a fixed top bar (address search plus "Filter"), a bottom sheet for details and lists, and large zoom +/- buttons at the right. Desktop: map plus a 380px side panel with the same content.
- Always offer a "List view" toggle. It lists the same requests, sorted by distance or date, and is fully usable without the map. This helps screen-reader users, keyboard users, and anyone who finds maps hard.

## 2. How requests and statuses are drawn
Rule: never rely on colour alone. Each status or category is encoded by shape and label as well as colour.

- Marker = category glyph inside a large pin or circle (about 36px visual, 48px hit area): pothole (road-surface icon), light (lamp), drain (grate). The same icons appear in the legend and filters, each with a word.
- Status = fill and outline treatment plus a colour-blind-safe palette, with a small badge:
  - Reported (received): hollow/white fill, dark outline, dot badge. Colour: amber.
  - In progress (being fixed or scheduled): half-filled, wrench badge. Colour: blue.
  - Fixed (resolved): solid fill, tick badge, slightly faded and smaller. Colour: green/teal.
  - Cannot fix or closed (rejected or duplicate): grey, cross badge, hidden by default.
  Check against deuteranopia, protanopia and tritanopia. All marker edges meet 3:1 against the basemap, and the status text on cards meets 4.5:1 or better.
- Default view shows open items plus items fixed in the last 30 days (a "recently fixed" reassurance), with a filter to show older ones. This avoids a map full of old green dots.
- Clustering: at low zoom, group markers into numbered circles (large numbers, a count rather than colour-coded). Tap zooms in. Clusters show a mini status breakdown only in the list, not on the map. Do not use heatmaps for the public view because they hide individual cases.
- Overlap: identical-location reports are merged into one marker with a count ("3 reports here"). A tap opens a list of them.
- Highlight: the selected marker gets a thick high-contrast ring and grows; others stay as they are. Do not dim the whole map heavily.
- Legend: always reachable by a labelled "Key" button, and a one-line status key in the filter sheet. Do not hide the meaning behind a tooltip.
- Motion: no pulsing or bouncing markers. Respect prefers-reduced-motion; fly-to animations become instant jumps.

## 3. Interaction
- Opening: map centred on the user's area (ask for location only after a tap on "Use my location", with a clear reason; fall back to the council boundary and an address/postcode search). Never prompt for permission on load.
- Search: address or postcode with autocomplete, plus a "reference number" box so someone can look up their own report.
- Filters: a single sheet with big toggles: category (3 to 4 icons with words), status, "reported in the last 7 / 30 / 90 days". Show the active filter count and a clear "Reset" button. Results update live with a visible count ("42 problems shown").
- Gestures: single-finger pan, pinch or buttons to zoom, double-tap zoom optional. Do not hijack page scroll on mobile: the map embedded in a page needs a clear way out (a "Skip map" link and no scroll trap).
- Keyboard: markers are focusable in a logical order (nearest first) with visible 3px focus outlines; Esc closes the sheet. Screen readers get an aria-live count update and the list view as an equivalent.
- Performance: vector or tile-based data, load only the viewport, cluster server-side or client-side beyond roughly 500 points. Works on a slow 3G connection, with a skeleton state, an explicit error message ("We could not load the map. Try again" plus the list/table alternative), and an empty state ("No problems match. Clear filters").

## 4. What a tap shows
Phone: the bottom sheet rises to about 45% of the screen (swipe up for full, with a labelled "Close" button), and the map stays visible with the selected pin. Desktop: the side panel. No tiny map popups.

Content order, plain language:
1. Category icon and title, such as "Pothole" with a street name or nearest address (rounded to the street or block, see privacy below).
2. Status as a large badge with an icon and words: "In progress: repair booked for 24 Nov".
3. Progress tracker: a 3 or 4 step line (Reported, Checked, Being fixed, Fixed) with dates, current step emphasised, and text equivalents.
4. Reported date, last updated date, and an expected date when it is known (shown as "expected", not promised).
5. Short description written or approved by staff, and a photo if available (with alt text, tap to enlarge).
6. Reference number with a "Copy" button, plus "Follow this problem" (email or SMS updates, no account required) and "Report a similar problem" or "I can see this too" if the council wants confirmation counts.
7. A "Directions / zoom to this" button and a link to the full page with a permanent URL for sharing.
Resolved items show who fixed them (the team, not individuals) and the fixed date. Rejected items state the reason in kind, plain wording ("Not a council road. Passed to the road owner").

Deep links: each request has a stable URL that opens the map on it, so a resident can bookmark it or follow a link from an email.

## 5. Things to be careful about
- Privacy: do not show reporter names, contact details, or exact home addresses. Snap points to the street or a 10 to 20 m offset where a report could identify a household. Strip EXIF location and faces or number plates from photos, and moderate free-text. Publish a short privacy note.
- Safety and misuse: do not display sensitive report types (for example anything flagged as hazard involving a specific vulnerable person, or crime). Rate-limit the API and add a delay to the publishing of new reports so staff can screen them.
- Honesty about status: show "last updated" everywhere and flag stale data ("Not updated in 30 days"). Never show "fixed" before staff confirm. Data refresh interval stated in the footer. Wrongly-optimistic dates damage trust more than no date.
- Accessibility and older users: contrast, 200% zoom, no timeouts, no reliance on colour, no drag-only actions, clear language at about reading age 9 to 12, and an alternative channel (phone number and "Call us" link) on every screen. Test with real older residents and with a screen reader (VoiceOver and TalkBack), not just automated audits.
- Languages: multiple languages if the area needs them, with right-to-left support where applicable. Dates in a local, unambiguous format ("24 Nov 2026").
- Cognitive load: at most three controls competing on screen at once; no onboarding carousels. A single dismissable one-line hint on first visit.
- Data quality: wrong categories or misplaced pins will happen. Add a "Something wrong with this entry?" link that goes to the council, not a public comment thread (avoids moderation burden and abuse).
- Basemap and licensing: attribution visible but unobtrusive; use a provider whose terms allow public sector use; consider self-hosted tiles for cost and privacy (no third-party tracking of residents' locations).
- Offline and weak signal: cache the last loaded view, show a banner when offline, keep the list readable.
- Expectation setting: a short, visible note on what the map is (reported problems, not emergencies) with "Emergency? Call ..." for urgent hazards.

## 6. Validation plan
- Prototype the bottom sheet, marker set and filter sheet; test with 5 to 8 users aged 65+ on their own phones, with tasks: find a problem on your street, tell whether it is fixed, find out when it will be.
- Run colour-blind simulation on markers, a Lighthouse/axe pass, and a slow-network test.
- Success measures: task completion without help above 90%, no key task over about 30 seconds, and fewer "what is happening with my report?" calls to the council.
