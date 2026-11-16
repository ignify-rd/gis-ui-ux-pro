# Answer key for review-sample.html (graders only)

Exactly five planted issues. Line numbers refer to `review-sample.html`.

| # | Line | Defect | Expected rule |
|---|------|--------|---------------|
| 1 | 41 | `attributionControl: false`, nothing re-adds attribution | C01 |
| 2 | 63 | `popup.setHTML(feature.properties.note)`, untrusted attribute as HTML | I10 |
| 3 | 66 | Popup shows `owner` and `phone` (data fetched at lines 27-31) to all users | I11 |
| 4 | 54-55 | Blue-cyan-green-yellow-red `interpolate` on raw `count` | S08 |
| 5 | 71-73 | `dayjs(...).startOf('day')` is local midnight; sent to the API as-is | T10 |

Grading: all five found with the rule id, and no invented defects counted as findings. Minor remarks (for example a missing map legend) are not planted and must be labelled low severity or optional.
