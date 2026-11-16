# Eval results 0.1.0

Six runs (sonnet): each scenario once following `SKILL.md` (with) and once without it (base). Graded strictly against the checks in `scenarios.md`: a check counts only if the output clearly states it. Raw outputs for scenarios 1 and 3 are in `runs-0.1.0/`.

**Totals: with skill 21/24, baseline 19/24.**

## Scenario 1: vessel detection dashboard (with 6/8, base 7/8)
| Check | with | base |
|---|---|---|
| Dark/unmatched distinct, not colour alone | yes | yes |
| Confidence threshold slider | yes | yes |
| Scene date/time shown | yes | yes |
| "Dark is not illegal" | yes | yes |
| AIS interpolated to SAR time and match radius stated | no (time offset yes, radius only as an unspecified "max distance" parameter) | yes (500 m / 30 min gate example) |
| SAR false-positive sources and evidence review | yes | yes |
| Legend covers all classes incl. unmatched, plus per-layer source/provenance | no (legend yes, per-layer source no) | no (same) |
| List linked to map | yes | yes |

## Scenario 2: review of a private app screen (omitted from the public repo)
Score: with 7/8, base 6/8. Details are not published because they describe private code.

## Scenario 3: InSAR landslide symbology (with 8/8, base 6/8)
| Check | with | base |
|---|---|---|
| Diverging ramp centred on 0 | yes | yes |
| Symmetric clamp, legend shows clamp and clipping | yes (+/-10, "<-10" / ">+10") | no (clamp +/-20 and open ends, but legend clipping not stated) |
| Per-point time series | yes | yes |
| LOS explained with asc/desc caveat | yes | yes |
| Reference point and time span | yes | yes |
| Coherence filter and "no points is not stable" | yes | yes |
| Warns against rainbow, CVD-safe scheme | yes | no (CVD-safe yes, no rainbow warning) |
| Context layers (slope, inventory, roads) | yes | yes |

## Notable differences
- The skill helped most where it holds specific rules: rule ids and checklist items in the review scenario, the rainbow warning, symmetric clamp and legend (S3), and the explicit sourced/synth labelling in all three runs. No synth content was presented as fact, and no wrong blueprint match was seen (maritime-awareness, surface-water-drought and ground-deformation were the right matches).
- Scenario 1 was a slight loss: the baseline stated a concrete match gate (500 m, 30 min) and the skill run did not. The skill's maritime problem had no rule about it.
- In the review scenario both runs missed an unlabelled no-data state painted as "normal". The with-skill run read the surface-water blueprint's "no-data distinct from no-water" pitfall but did not apply it.

## Fixes made (data gaps the skill should cover)
- New rule S18 "No-data gets its own legend class" (synth), attached to `surface-water-drought`.
- New rule D10 "Source and date per layer, readable without hover" (synth), attached to `maritime-awareness` and `surface-water-drought`.
- New rule E09 "State the AIS match gate and time offset" (synth), attached to `maritime-awareness`.
- `references/quick-reference.md` and `checklist.md` regenerated. Verified through search and `--blueprint` output (see the task report).

## Known gaps
- The new rules are not re-evaluated by a fresh agent run. The fix is verified only by search and blueprint output.
- No numeric default for the AIS gate is given in the data. E09 only says to state it, because no sourced value exists.
