# Route vs native, per point

## R6 rerun, 2026-11-03 (current code, all 12 cells; details in RESULTS-R6.md)

All 12 cells pass: total p.e. within 1 % and 3 sigma (route/native 0.9988-1.0047, |z| <= 1.47); KS p >= 0.023;
|mean time difference| <= 0.030 ns; route-vs-native pixel correlation within 0.0038 of the native seed pair; determinism
pass. Per-cell files: `R6_<TEL>_za<ZA>.json`; pixel-list counts `R21_<TEL>_za<ZA>.json`.

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

## Earlier run (before R19 and R21 fixes; kept for reference)


20 deg passes; 40/60 deg fail from too little atmospheric absorption in the route (R19, fix in progress; see RESULTS.md).
Pixel correlation equals the native-vs-native control, so it does not separate route from native.
Determinism: bunch files and p.e. content identical for all points.

| telescope | zenith | route/native total p.e. | 1 sigma | gate | per-event ratio | pixel corr (n events) | control | pixels >3 sigma (route / control) | mean time diff [ns] | KS D, p |
|---|---|---|---|---|---|---|---|---|---|---|
| LSTS-01 | 20 | 1.0026 | 0.0023 | PASS | 1.0017 | 0.9746 (48) | 0.9692 | 29 / 43 | -0.013 +- 0.017 | 0.0052, 0.0409 |
| MSTS-04 | 20 | 1.0034 | 0.0020 | PASS | 1.0013 | 0.9543 (41) | 0.9547 | 23 / 29 | -0.058 +- 0.042 | 0.0040, 0.833 |
| LSTN-01 | 20 | 1.0023 | 0.0020 | PASS | 1.0032 | 0.9621 (48) | 0.9594 | 32 / 35 | -0.035 +- 0.021 | 0.0044, 0.125 |
| MSTN-07 | 20 | 1.0043 | 0.0018 | PASS | 1.0047 | 0.9551 (30) | 0.9512 | 20 / 44 | +0.017 +- 0.050 | 0.0079, 0.138 |
| LSTN-01 | 40 | 1.0705 | 0.0017 | FAIL | 1.0715 | 0.9711 (50) | 0.9709 | 29 / 40 | -0.011 +- 0.021 | 0.0081, 0.0022 |
| MSTN-07 | 40 | 1.0763 | 0.0020 | FAIL | 1.0750 | 0.9549 (37) | 0.9521 | 8 / 20 | +0.046 +- 0.068 | 0.0087, 0.248 |
| LSTS-01 | 60 | 1.3823 | 0.0038 | FAIL | 1.3875 | 0.9904 (50) | 0.9861 | 110 / 14 | -0.041 +- 0.014 | 0.0075, 0.156 |
| MSTS-04 | 60 | 1.3946 | 0.0029 | FAIL | 1.3897 | 0.9850 (50) | 0.9795 | 44 / 5 | +0.013 +- 0.034 | 0.0069, 0.862 |
| LSTN-01 | 60 | 1.3327 | 0.0041 | FAIL | 1.3371 | 0.9811 (50) | 0.9760 | 81 / 14 | -0.026 +- 0.033 | 0.0062, 0.481 |
| MSTN-07 | 60 | 1.3445 | 0.0041 | FAIL | 1.3334 | 0.9774 (41) | 0.9715 | 20 / 4 | +0.048 +- 0.041 | 0.0182, 0.0837 |
