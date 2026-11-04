# R6 stream validation (route in stream mode)

Stream variant of `scripts/run_r6_point.sh`: the CORSIKA IACT file is piped into `shower_route --input - --output -`,
whose output is piped into sim_telarray (`Bypass_Optics=1`, positional `-`). Script: `scripts/run_r6_stream_point.sh`.
Route seed 11, native seeds 4242-4244 (reused from the disk matrix), same CORSIKA IACT input. Raw: `results/R6-stream_<TEL>_za<ZA>.json`.
Stream route outputs: `work/<TEL>_za<ZA>/route_r6s/`; compare.py run with route tag `r6s`.
Each stream route ran once (no repeat, no determinism check).

| cell | route p.e. (stream) | native mean (seeds 4242-4244) | route/native | 1 % / 3 sigma | matched events | pixel corr route | pixel corr control (native 4243 vs 4242) | disk vs stream |
|---|---|---|---|---|---|---|---|---|
| LSTS-01 20 deg | 1677207 | 1678606.0 | 0.99917 | pass / pass | 492 | 0.9733 | 0.9700 | identical |
| MSTN-07 20 deg | 379875 | 379051.7 | 1.00217 | pass / pass | 299 | 0.9516 | 0.9502 | identical |
| LSTS-01 60 deg | 390761 | 390241.7 | 1.00133 | pass / pass | 500 | 0.9901 | 0.9874 | identical |
| MSTN-07 60 deg | 95157 | 95094.7 | 1.00066 | pass / pass | 386 | 0.9715 | 0.9707 | identical |

Disk values (`results/R6_<TEL>_za<ZA>.json`) are identical to the stream values in all four cells: route p.e., route/native
ratio, matched events, pixel correlation and per-event p.e. ratio. The stream route output is a separate file
(`route.simtel.zst` differs byte-wise from the disk one; the stream has no bunch file); the identical counts follow
plausibly from the same seeds (the bunch content was not compared), not from a reuse of disk files.

Pass criteria as in `RESULTS-R6.md`: all four cells pass the 1 % and 3 sigma checks for total p.e.; the
pixel correlation of stream and disk routes is the same as the disk values, so the route-minus-control test holds
as in disk mode.

Not run for stream: arrival-time KS test and determinism repeat (the disk matrix covers them).
