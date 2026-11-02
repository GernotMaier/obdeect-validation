# P10 benchmark: shower route speed (arm64 only)

Summary:
- Route + sim_telarray (`Bypass_Optics=1`) takes 1.28x (LSTS-01) and 1.46x (MSTS-04) the wall time of native sim_telarray.
- These runs used files (disk mode). gzip of the camera file (about 38 MB/s, about 12 s of 27 s) dominates the route IO. Stream mode writes uncompressed to a pipe, where reader and writer costs were measured as negligible (`val/phase3/streamperf/RESULTS.md`). An end-to-end stream benchmark has not been run.
- The route scales only 1.39x on 6 threads: tracing parallelises, the writer and gzip are serial.
- Apple M3 Pro, arm64 Linux container, 6 CPUs, 2 GB. The container was shared with other jobs, so timings are noisy (median and min given).

Input: 50 showers, 1 TeV gamma, zenith 20 deg. LSTS-01: 40.65 M photons (8.2 M bunches); MSTS-04: 19.28 M photons (3.9 M bunches).

## Per stage (wall s, median of 3, min in brackets)

| stage | LSTS-01 | MSTS-04 |
|---|---|---|
| (a) native sim_telarray | 47.5 (40.7); 1.17 us/photon | 27.5 (27.4); 1.43 us/photon |
| (b) route, 1 thread | 27.0 (26.0); 0.66 us/photon | 14.5 (14.2); 0.75 us/photon |
| (c) sim_telarray `Bypass_Optics=1` | 33.7 (33.6); 0.83 us/photon | 25.6 (25.0); 1.33 us/photon |
| (b)+(c) | 60.7 = 1.28x (a) | 40.1 = 1.46x (a) |

Route (b) split (LSTS-01, 1 thread): model loading ~20 %, tracing ~34 %, writer and IO ~45 %.

## Thread scaling (LSTS-01 route)

| threads | 1 | 2 | 4 | 6 |
|---|---|---|---|---|
| wall s | 27.0 | 21.7 | 19.7 | 19.5 |
| speed-up | 1.0 | 1.24 | 1.37 | 1.39 |

The tracing kernel alone scales 5.1x on 6 threads (305.6 -> 57.4 ns/photon). Three concurrent single-thread routes
give 2.8x the throughput of one.

## Writer

The new zero-copy writer is ~25 % faster than the old one for uncompressed output (1495 vs 1184 MB/s), with identical content.
With gzip both run at ~38 MB/s; gzip is the bottleneck.

## Limits

- No production (x86-64) numbers; do not use these as production speed-up claims.
- Installed obdeect package was built 2026-10-29, not the current HEAD 62f1862.
- N=6 concurrent routes not run (memory guard).

Raw data: `results/*.jsonl`, load snapshots `results/load.log`; scripts in `scripts/`.
