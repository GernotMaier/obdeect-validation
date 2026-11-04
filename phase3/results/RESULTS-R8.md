# R8: MSTS-04 at shower azimuth 90 and 180 deg (phi != 0), 20 deg zenith, 2026-11-03

Own CORSIKA run per azimuth (50 showers, same settings as the za20 point, `scripts/run_corsika_az.sh`), telescope
pointing phi = shower azimuth in native and route (`scripts/run_r8_az.sh`). Native seeds 4242-4244, route seed 11.
Model 7.0.0 (za20 export reused, no azimuth dependence). The earlier totals in tasks.md (1.0024 / 1.0004) were not
on disk and are not reproduced; these are the new records.

## Totals (gate: 1 % and 3 sigma)

| azimuth | native p.e. (seeds 4242/4243/4244) | route p.e. | route/native | sigma [%] | z | 1 % | 3 sigma |
|---|---|---|---|---|---|---|---|
| 90 deg | 591414 / 589564 / 590424 | 589370 | 0.9981 | 0.16 | -1.17 | pass | pass |
| 180 deg | 551039 / 548041 / 547604 | 549764 | 1.0016 | 0.24 | +0.66 | pass | pass |

## Per-event arrival times (matched events; per event mean p.e. time, route minus native 4242)

| azimuth | matched events | mean dt [ns] +- SEM | SD [ns] | events with abs(dt) > 0.2 ns | native 4243 minus 4242: mean +- SEM, SD, count > 0.2 ns | pooled per-p.e. KS p |
|---|---|---|---|---|---|---|
| 90 deg | 438 | -0.032 +- 0.017 | 0.34 | 145 | -0.028 +- 0.016, 0.35, 147 | 0.46 |
| 180 deg | 446 | -0.029 +- 0.015 | 0.32 | 153 | -0.038 +- 0.015, 0.32, 137 | 0.023 |

Files: `R8_MSTS-04_za20_az<AZ>.json` (totals, pixel correlation), `R8_times_MSTS-04_za20_az<AZ>.json` (per-event
times), `R8_control_native_pair_az<AZ>.json` (native seed pair, same per-event method).

Verdict: pass. Totals within 1 % and 3 sigma. The route-minus-native per-event mean is -0.03 ns (within 0.2 ns), the
same as the native seed-pair offset (-0.03 to -0.04 ns). The per-event scatter (SD 0.32-0.34 ns, and 145-153
events above 0.2 ns) equals the native seed-pair scatter (0.32-0.35 ns, 137-147 events). The per-event test is
therefore not able to show a route-specific difference at this statistics; it shows none.
The pooled KS p at 180 deg is 0.023 (> 1e-3, pass); the per-event method does not depend on it.
Pixel correlation (route vs native 4242) 0.958 / 0.957, native pair 0.959 / 0.958.
