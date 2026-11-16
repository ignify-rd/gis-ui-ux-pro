# Eval results 0.2.0

Eight runs for the new scenarios 4-7. Each scenario was run once following `SKILL.md` (with) and once without it (base), each by a fresh subagent. Graded strictly against the checks in `scenarios.md`: a check counts only if the output clearly states it. Raw outputs are in `runs-0.2.0/`. The runs contained no local paths or private names, so they are committed unchanged.

**Totals (scenarios 4-6): with skill 21/24, baseline 13/24.** Scenario 7: re-run pending.

## Scenario 4: civic service-requests map (with 6/8, base 4/8)
| Check | with | base |
|---|---|---|
| Restrained named direction, subtle | yes (Civic Paper, subtle) | no (calm civic tone, but a generic default, no named direction) |
| Plain safe baseline next to the direction | yes | no |
| Status not colour-only, legend covers every status | no (status marks and words yes; the only legend is the sentence legend "Each marker = one report", no entry per status) | yes (fill, outline and badge per status; "Key" button and status key in the filter sheet, icons with words) |
| PII hidden and omitted from query and export | yes ("omit those fields from the public query itself"; checklist covers exports) | no (hidden from display only, query and export not mentioned) |
| Popup content as text, not raw HTML | yes (I10) | no (free text moderated, HTML rendering not mentioned) |
| No bold motion, reduced-motion path | yes (A13, no pulsing) | yes |
| Attribution visible on load and findable after collapse | no (visible on load only) | no ("visible but unobtrusive") |
| Touch targets, text size and contrast | yes (44 px, 16 px, 4.5:1 and 3:1) | yes (48 px, 18 px, 4.5:1 and 3:1) |

## Scenario 5: harbour fleet operations screen (with 7/8, base 4/8)
| Check | with | base |
|---|---|---|
| Two or more directions plus a neutral baseline | yes (Signal Track, Night Ops, Civic Paper baseline) | no |
| Distinctive element in marker grammar or hero replay, balanced | yes (replay scrubber as hero, heading glyphs) | no |
| Data ramps from palettes, control positions conventional | yes (palette ids and hexes quoted, S19, corners locked) | no |
| Per-vessel freshness with UTC or explicit zone | yes (UTC with local offset, age tiers) | yes (age tiers; "time is always shown with its zone") |
| Status not colour-only, legend covers each state | no (shape, badge and fade yes; legend "with the age encoding" but no entry per status stated) | no (no legend mentioned) |
| Density handling and list-map linked selection | yes | yes |
| Replay: play/pause, scrubber, speed, visible current time | yes | yes |
| Limited motion with a reduced-motion alternative | yes (A13: stepwise jumps, static ring for pulse) | no (single pulse, no reduced-motion path) |

## Scenario 6: Cesium pre-sales 3D story (with 8/8, base 5/8)
| Check | with | base |
|---|---|---|
| Expressive cinematic look at bold level, data readable | yes (Urban Twin, bold) | yes (golden hour, premium globe, muted context) |
| Cesium credits and ion logo visible, data attribution intact | yes | no (credits kept visible, ion logo not named) |
| 2D or static fallback for no WebGL or weak GPU | yes (2D toggle, static image without WebGL) | no (video backup for network failure, lower resolution on mobile; no 2D or static fallback) |
| Reduced motion: cuts or fades, with a pause control | yes (setView, crossfade, pause button) | no (crossfades yes; "pause on any input" for auto-play only, and an always-on orbit drift) |
| Vertical exaggeration labelled | yes | yes |
| Distance types distinguished and labelled | yes (straight line vs ellipsoid surface vs routed) | yes (straight-line vs by road) |
| Keyboard and non-scroll navigation | yes | yes |
| Performance cautions | yes | yes |

## Scenario 7: review of the synthetic page (re-run pending)
The first S7 runs were withdrawn. Planted issue 5 was not a real defect: `startOf('day').toISOString()` converts local midnight to UTC, which is what T10 asks for. The sample now sends zone-less wall-clock strings (`format('YYYY-MM-DDTHH:mm:ss')`) at line 73, and `ANSWER_KEY.md` row 5 was updated. Both S7 runs are being re-run against the fixed sample. They will be graded here after the re-run.

## Signature behaviour (scenarios 4-6, with skill)
| | S4 | S5 | S6 |
|---|---|---|---|
| Led with the 5-line summary | yes | yes (in a code block, after the title) | yes |
| Two directions plus a safe baseline | yes (Civic Paper, Canvas Studio, baseline) | yes (Signal Track, Night Ops, baseline) | yes (Urban Twin, Canvas Studio, baseline) |
| Locked conventions stated | yes | yes | yes (in the self-critique) |

Baselines: all three were competent but generic. None named a visual direction, offered alternatives or a fallback look, or separated data colours from style. S5 base described one dark theme. S6 base came closest to a distinct look (golden-hour lighting, desaturated surroundings, outline highlight) but treated it as one fixed proposal. Baselines were often strong on product detail: S4 base had an emergency note and a phone channel, and S5 base had hatched data gaps on the timeline and keyboard shortcuts.

## Notable differences
- The largest gains came from specific rules and the signature layer: query-level PII removal (I11), text-only popups (I10), reduced-motion paths (A13), the Cesium credit, exaggeration and 2D-fallback cautions, and rule ids in the review.
- S6 was the only scenario with no matching playbook. The run picked `site-suitability` as the closest problem and said so, then drew most content from the Cesium stack rows (cs-01 to cs-09). It still scored 8/8.
- Legends were the common miss. In S4 the Civic Paper hero ("legend written as a sentence") replaced a per-status key, and no rule asked for an entry per class. The baseline S4 run did better here.
- S7 notes are pending the re-run. The old runs showed two things. The skill run raised optional absent features (a legend) to critical. The sample also had unplanted real bugs, which are now listed in `ANSWER_KEY.md` as not penalised.

## Fixes made (data and skill gaps the runs revealed)
- S14 "Legend reflects what is drawn" now also asks for one entry for every class or state drawn (each status, stale, unmatched, no data) with the map's icon or shape. The checklist question was updated to match.
- S14 was added to `service-requests` and `fleet-tracking`, so their blueprints carry the legend rule and checklist item.
- C01 was added to `service-requests`, so its blueprint carries "findable after it collapses". The S4 run took attribution only from the locked-conventions list, which says "visible".
- SKILL.md review workflow, step 7: findings are defects in what the code does. Accessibility (keyboard, text alternative, contrast, colour-only meaning), privacy, attribution and security gaps always stay in the severity-ordered findings, even when the feature is absent. Only optional features the page never attempts (search, legend extras, table view) go last in an "Also consider (low, optional)" list, unless the user asked for a full audit.
- S14 was also added to `disaster-response` and `maritime-awareness`.
- `review-sample.html` line 73 now makes planted issue 5 a real T10 violation (zone-less local strings). `ANSWER_KEY.md` row 5 was updated and the key now lists the sample's known incidental bugs, and the broken nested backticks in `scenarios.md` line 3 were fixed. No scenario expectation changed.
- `references/quick-reference.md` and `checklist.md` were regenerated (`build_reference.py --check` passes). The validator and all 80 tests pass, and SKILL.md is 203 lines.

## Known gaps
- No fresh agent has re-run these fixes. They are verified only through blueprint output (S14 and C01 now appear for `service-requests`).
- Step 7 of the review workflow has not yet been verified by a fresh S7 run.
- S6 has no scroll-story or presentation playbook. The run had to use `site-suitability` plus the Cesium stack.
- The S7 sample still contains its unplanted bugs. They are now documented in the answer key instead of being fixed, because fixing them would need new runs.
