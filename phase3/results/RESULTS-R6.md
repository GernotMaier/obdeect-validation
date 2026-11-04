# R6 validation matrix, rerun 2026-11-03 (current code, all 12 cells)

Route: `shower_route` CLI (disk mode: bunch file, then sim_telarray `Bypass_Optics=1`), seed 11, repeated once
(`r6rep`); native sim_telarray `Bypass_Optics=0`, seeds 4242/4243/4244. Same CORSIKA IACT inputs and seeds as the
earlier matrix (`work/<TEL>_za<ZA>/gamma_*.iact`, not regenerated). 1 TeV gamma, azimuth 0, 50 showers, model 7.0.0.
Scripts: `scripts/run_r6_matrix.sh` (one lane per site), `scripts/run_r6_point.sh`, `scripts/compare.py`,
`scripts/determinism.py`, `scripts/pixel_list_check.py` (R21 counts). Raw per cell: `results/R6_<TEL>_za<ZA>.json`.
Versions: simtools worktree `wt/simtools-p3` (uncommitted, via PYTHONPATH), obdeect `air-shower-photons`
(reinstalled in the container before the run), sim_telarray 2026.124 in container `obdeect-val`.

## Acceptance (plan) and verdict

| criterion | result over 12 cells |
|---|---|
| total p.e. route/native within 1 % | pass 12/12; range 0.9988-1.0047 |
| within 3 sigma (sigma = sqrt(native SEM^2 + route Poisson^2)) | pass 12/12; largest |z| 1.47 (MSTN-07 40 deg) |
| arrival times, KS p > 1e-3 (per-p.e. times, matched events) | pass 12/12; smallest p 0.023 (LSTS-01 20 deg) |
| arrival times, mean difference < 0.2 ns | pass 12/12; |mean dt| <= 0.030 ns |
| QE applied once | see `bypass-test/results.txt` (QE 0.5 scaling: detected 0.5004 ratio; unchanged by this rerun) |
| pixel correlation consistent with native seed-to-seed control | consistent: route - control within -0.0015 to +0.0038 (control = native 4243 vs 4242, one pair per cell) |
| determinism (two route runs, same seed) | pass 12/12: bunch files byte-identical; p.e. content identical |
| every telescope event has a pixel list (R21) | pass 12/12: see `results/R21_<TEL>_za<ZA>.json` |

Note: `compare.py` still writes `pass_all` with the old gate (pixel correlation > 0.99), which fails by design
since the native control is 0.95-0.99; the verdict above uses the redefined gate.
Pixels outside 3 sigma (route vs native, pooled seeds): route 6-152 per cell, control native pair 12-249 per cell;
this is a count of noisy pixels, not a gate.

## Table

| telescope | zenith | native mean [p.e.] | route [p.e.] | route/native | sigma [%] | (ratio-1)/sigma | 1 % | 3 sigma | KS p (per-p.e.) | mean dt [ns] +- SEM | pixel corr route (native seed pair) | route - control | matched events |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| LSTS-01 | 20 | 1678606 | 1677207 | 0.9992 | 0.23 | -0.37 | pass | pass | 0.023 | -0.017 +- 0.006 | 0.9733 (0.9700) | +0.0033 | 492 |
| MSTS-04 | 20 | 603210 | 603711 | 1.0008 | 0.20 | +0.42 | pass | pass | 0.210 | -0.024 +- 0.015 | 0.9559 (0.9574) | -0.0015 | 438 |
| LSTN-01 | 20 | 1461848 | 1461028 | 0.9994 | 0.20 | -0.28 | pass | pass | 0.588 | -0.020 +- 0.008 | 0.9657 (0.9623) | +0.0034 | 488 |
| MSTN-07 | 20 | 379051 | 379875 | 1.0022 | 0.18 | +1.18 | pass | pass | 0.638 | -0.025 +- 0.021 | 0.9516 (0.9502) | +0.0014 | 299 |
| LSTS-01 | 40 | 1196284 | 1197360 | 1.0009 | 0.21 | +0.42 | pass | pass | 0.506 | -0.021 +- 0.004 | 0.9811 (0.9779) | +0.0031 | 500 |
| MSTS-04 | 40 | 406894 | 406417 | 0.9988 | 0.32 | -0.37 | pass | pass | 0.079 | -0.027 +- 0.015 | 0.9697 (0.9694) | +0.0002 | 491 |
| LSTN-01 | 40 | 1061542 | 1062029 | 1.0005 | 0.18 | +0.26 | pass | pass | 0.313 | -0.026 +- 0.006 | 0.9737 (0.9702) | +0.0035 | 500 |
| MSTN-07 | 40 | 264967 | 265766 | 1.0030 | 0.21 | +1.47 | pass | pass | 0.586 | +0.018 +- 0.020 | 0.9573 (0.9584) | -0.0011 | 352 |
| LSTS-01 | 60 | 390241 | 390761 | 1.0013 | 0.39 | +0.34 | pass | pass | 0.219 | -0.017 +- 0.006 | 0.9901 (0.9874) | +0.0027 | 500 |
| MSTS-04 | 60 | 134511 | 135149 | 1.0047 | 0.32 | +1.46 | pass | pass | 0.632 | -0.030 +- 0.012 | 0.9872 (0.9861) | +0.0011 | 500 |
| LSTN-01 | 60 | 325837 | 325495 | 0.9990 | 0.42 | -0.25 | pass | pass | 0.902 | -0.016 +- 0.009 | 0.9811 (0.9773) | +0.0038 | 500 |
| MSTN-07 | 60 | 95094 | 95157 | 1.0007 | 0.44 | +0.15 | pass | pass | 0.490 | -0.017 +- 0.023 | 0.9715 (0.9707) | +0.0008 | 386 |

Mean dt is the per-event mean of p.e. arrival times, route minus native seed 4242 (SEM from events).
Route-vs-control: route pixel correlation minus the correlation of native seed 4243 with 4242 on the same events.

## Notes

- Matched events are fewer than the route events where the route and native trigger on different events
  (for example MSTN-07 20 deg: 299 matched events); only matched events enter the event-level tests.
- All cells, including South 40 deg (not run before), were run with the current code. Native means reproduce the
  earlier values exactly (same seeds), e.g. LSTS-01 20 deg 1678606 p.e.
- The earlier results (`RESULTS.md`, `RESULTS-R19.md`, `RESULTS-R19-pixels.md`) are kept.
