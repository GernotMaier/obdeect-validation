# obdeect route vs native sim_telarray, by zenith (phase 3, P9 / R6)

## Current status (R6 rerun, 2026-11-03)

- The full matrix was rerun with the current code: 4 telescopes x 20/40/60 deg, 12 cells (South 40 deg was missing
  in the earlier results and is now run). All 12 cells pass the plan acceptance: total p.e. within 1 % and 3 sigma,
  KS p >= 0.023, |mean dt| <= 0.030 ns, pixel correlation within 0.0038 of the native seed pair, determinism identical.
  Details: `RESULTS-R6.md`; table: `summary_table.md`; raw: `R6_<TEL>_za<ZA>.json`.
- The sections below are the earlier run (before the R19 fix), kept for reference. The pixel gate in them
  (correlation > 0.99) is superseded by the native-control gate.

Summary:
- **20 deg passes.** Total photo-electrons (p.e.) of the route agree with native within 0.4 % for all four telescopes.
- **40 and 60 deg failed in this run** (route/native 1.07-1.08 and 1.33-1.39). Cause (R19): with `Bypass_Optics=1`
  sim_telarray takes the airmass from the camera-frame bunch direction (airmass ~1), so it applied too little absorption.
  **Fixed:** the route now scales each bunch by the missing transmission. All 9 rerun points pass (0.999-1.005):
  see `RESULTS-R19.md`.
- Times and determinism pass. The pixel gates cannot separate route from native (see below).

Raw results: `results/<TEL>_za<ZA>.json`; full table: `results/summary_table.md`; photon/bunch counts: `results/inventory.txt`.
Versions: obdeect 62f1862, simtools a361838 (dirty, incl. untracked `shower_route.py`), model 7.0.0, sim_telarray 2026.124.

## Setup

- 1 TeV gamma, azimuth 0, 50 showers per point, 10 core reuses (500 telescope blocks). One CORSIKA IACT file feeds both chains.
- Native: sim_telarray `Bypass_Optics=0`, seeds 4242/4243/4244. Route: `shower_route` (seed 11), then sim_telarray `Bypass_Optics=1`.
- Input-plane height: minimum safe height rounded up to 0.1 m. Manual overrides at 60 deg: MSTS-04 40.0 m, MSTN-07 41.0 m (see open items).
- South 40 deg was not run (stopped after the South 60 deg failure).

## Total p.e. (native = mean of 3 seeds)

Gate: 1 % and 3 sigma, sigma_tot = sqrt(sem_native^2 + Poisson_route^2).

| telescope | zenith | native mean [p.e.] | route [p.e.] | route/native | gate |
|---|---|---|---|---|---|
| LSTS-01 | 20 | 1678606 | 1682950 | 1.0026 | pass |
| MSTS-04 | 20 | 603211 | 605257 | 1.0034 | pass |
| LSTN-01 | 20 | 1461848 | 1465275 | 1.0023 | pass |
| MSTN-07 | 20 | 379052 | 380694 | 1.0043 | pass |
| LSTN-01 | 40 | 1061542 | 1136412 | 1.0705 | FAIL |
| MSTN-07 | 40 | 264967 | 285189 | 1.0763 | FAIL |
| LSTS-01 | 60 | 390242 | 539445 | 1.3823 | FAIL |
| MSTS-04 | 60 | 134511 | 187589 | 1.3946 | FAIL |
| LSTN-01 | 60 | 325837 | 434255 | 1.3327 | FAIL |
| MSTN-07 | 60 | 95095 | 127856 | 1.3445 | FAIL |

The per-event p.e. ratio tracks the total ratio (correlation 0.97-0.9998), so the excess is per event, not a seed effect.
Native seed spread is 0.12-0.66 %.

## Other tests

- **Times: pass.** Per-event mean time difference |dt| <= 0.06 ns; KS p >= 0.002 everywhere.
- **Determinism: pass.** Two route runs with the same seeds give byte-identical bunch files and identical p.e. content.
- **Pixel tests: not usable as written.** Route-vs-native pixel correlation (0.95-0.99) equals the native-vs-native control
  (0.95-0.97 at 20-40 deg) within 0.01. At 3-4 p.e. per pixel the >0.99 gate cannot be met by any independent simulation;
  it needs a different estimator. "Pixels outside 3 sigma" also fails for native seed pairs (4-44 pixels).
  At 60 deg the route is worse (44-110) because of the total excess.

## Open items

1. Zenith excess (R19): fix in progress, rerun 40/60 deg.
2. MSTS-04 and MSTN-07 at 60 deg: the route rejected the rounded minimum input-plane height. Cause (R20): the plane-height
   helper ignores the telescope axes offset. Fix in progress.
3. Pixel lists exist only for the first block per shower (R21), so pixel tests used 30-50 events per point.
   Expected fixed by the route writing one event per input event (R14); to verify.
4. MC shower header in the route output has placeholders (energy, direction, core). No effect on p.e. or times.
5. Pixel gate needs a Poisson-aware estimator.
