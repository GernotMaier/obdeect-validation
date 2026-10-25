"""Python trace() cost per input photon (best of three).

usage: bench_py.py <model.json> <photons> <threads> [outputs] [detected_only]
outputs: comma-separated column names, or "all"; detected_only: 0 or 1.
Run with PYTHONPATH set to the obdeect build under test.
"""

import sys
import time

from obdeect import OpticalModel

model = OpticalModel.load(sys.argv[1])
n, threads = int(sys.argv[2]), int(sys.argv[3])
extra = {}
if len(sys.argv) > 4 and sys.argv[4] != "all":
    extra["outputs"] = sys.argv[4].split(",")
if len(sys.argv) > 5:
    extra["detected_only"] = sys.argv[5] == "1"
photons = model.star_photons(n, seed=3, distance_m=1e4)
best = 1e9
for _ in range(3):
    start = time.perf_counter()
    model.trace(photons, seed=3, apply_responses=True, threads=threads, **extra)
    best = min(best, time.perf_counter() - start)
print(f"{1e9 * best / n:8.1f} ns per photon  threads={threads} {extra}")
