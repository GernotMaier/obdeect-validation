# R19 route: per-pixel, per-event and time comparison (9 points)

- Pixel correlation gate (route within 0.01 of native seed-vs-seed control): PASS, 9/9 (max |diff| 0.0038). Route has pixel lists for every event at all 9 points (R21 fixed). Pixels outside 3 sigma: route <= control at all 9 (reported, not gated).
- Image shape gate (centroid and width within control spread): PASS, 9/9.
- Time gate (|dt| < 0.1 ns): PASS, 9/9 (max |dt| 0.030 ns).

| telescope | zenith [deg] | matched events (with pixel lists) | PE sum ratio | PE Pearson | pixel corr route (control) | pixels >3 sigma route / control | shape: route dcx, dcy, drms [mm] (control sd) | dt [ns] | KS D, p (per-p.e. times) | gate |
|---|---|---|---|---|---|---|---|---|---|---|
| LSTS-01 | 20 | 492 | 0.9982 | 0.99986 | 0.9733 (0.9700), n=492 | 152 / 249 | -0.17, -0.25, -0.22 (4.8, 5.8, 10.4) | -0.017 +- 0.006 | 0.0016, 0.023 | PASS |
| LSTS-01 | 40 | 500 | 1.0010 | 0.99906 | 0.9811 (0.9779), n=500 | 96 / 197 | -0.60, +0.10, -0.22 (4.2, 4.5, 5.2) | -0.021 +- 0.004 | 0.0011, 0.51 | PASS |
| LSTS-01 | 60 | 500 | 1.0051 | 0.98347 | 0.9901 (0.9874), n=500 | 39 / 80 | -0.26, -0.07, +0.33 (3.6, 3.4, 7.2) | -0.017 +- 0.006 | 0.0024, 0.22 | PASS |
| MSTS-04 | 40 | 491 | 0.9967 | 0.99711 | 0.9697 (0.9694), n=491 | 21 / 40 | -0.37, +0.13, -0.06 (7.1, 6.5, 9.2) | -0.027 +- 0.015 | 0.0028, 0.079 | PASS |
| MSTS-04 | 60 | 500 | 1.0012 | 0.97156 | 0.9872 (0.9861), n=500 | 9 / 12 | -0.38, -0.20, -0.18 (3.5, 3.4, 7.8) | -0.030 +- 0.012 | 0.0029, 0.63 | PASS |
| LSTN-01 | 40 | 500 | 1.0014 | 0.99909 | 0.9737 (0.9702), n=500 | 104 / 164 | -0.29, -0.25, -0.30 (5.2, 5.4, 6.4) | -0.026 +- 0.006 | 0.0013, 0.31 | PASS |
| LSTN-01 | 60 | 500 | 1.0022 | 0.98635 | 0.9811 (0.9773), n=500 | 43 / 66 | -0.25, +0.02, -0.19 (4.0, 4.9, 9.0) | -0.016 +- 0.009 | 0.0014, 0.90 | PASS |
| MSTN-07 | 40 | 352 | 1.0022 | 0.99740 | 0.9573 (0.9584), n=352 | 13 / 23 | -0.86, -0.20, +0.81 (7.5, 7.1, 10.1) | +0.018 +- 0.020 | 0.0022, 0.59 | PASS |
| MSTN-07 | 60 | 386 | 0.9944 | 0.96637 | 0.9715 (0.9707), n=386 | 6 / 12 | -0.38, +0.13, -0.75 (4.9, 5.9, 11.6) | -0.017 +- 0.023 | 0.0041, 0.49 | PASS |

Route has pixel lists for all route events at all 9 points. The matched count is lower than the route event count at MSTN-07 because the route and native seeds trigger on different event sets; only matched events enter the tests.

Run: `scripts/compare.py` (route tag r19, native seeds 4242, 4243, 4244; 4242 is the reference, 4243 the control) in container `obdeect-val` for each point, sequentially. Shape: p.e.-weighted centroid and rms width per event from the camera geometry in the sim_telarray file, same events as the pixel tests, run from a scratch script outside the repo; gate is |mean route difference| <= control SD per component. Times: per-event mean of p.e. times, route minus native; KS on pooled per-p.e. times.
