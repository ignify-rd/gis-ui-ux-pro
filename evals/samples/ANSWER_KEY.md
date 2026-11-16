# Answer key for review-sample.html (graders only)

Exactly five planted issues. Line numbers refer to `review-sample.html`.

| # | Line | Defect | Expected rule |
|---|------|--------|---------------|
| 1 | 41 | `attributionControl: false`, nothing re-adds attribution | C01 |
| 2 | 63 | `popup.setHTML(feature.properties.note)`, untrusted attribute as HTML | I10 |
| 3 | 66 | Popup shows `owner` and `phone` (data fetched at lines 27-31) to all users | I11 |
| 4 | 54-55 | Blue-cyan-green-yellow-red `interpolate` on raw `count` | S08 |
| 5 | 71-73 | `dayjs(...).startOf('day')` local midnight sent as `format('YYYY-MM-DDTHH:mm:ss')`: a wall-clock string with no Z or offset, so the server cannot know the zone | T10 |

Known incidental bugs (not planted, not penalised if reported):
- Line 79: `map.getSource('districts').setData(data)` overwrites the district polygons with the `/api/requests` response.
- Lines 65-67: the owner `<p>` is appended to `popup.getElement()`, outside the popup content container.
- Lines 70-74: the date filter runs only on `change`, never on load, so the map does not match the preset date.

Grading: all five found with the rule id, and no invented defects counted as findings. Minor remarks (for example a missing map legend) are not planted and must be labelled low severity or optional.
