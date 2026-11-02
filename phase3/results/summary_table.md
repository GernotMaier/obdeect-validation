# Route vs native, per point

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
