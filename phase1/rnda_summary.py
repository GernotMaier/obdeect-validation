"""Summarise derive-mirror-rnda per-mirror results; compare backends on shared mirrors."""
import json
import sys

import numpy as np

runs = {name: json.load(open(path))["per_mirror_results"] for name, path in zip(sys.argv[1::2], sys.argv[2::2])}
for name, rows in runs.items():
    pct = np.array([r["percentage_diff"] for r in rows])
    rnda = np.array([r["optimized_rnda"] for r in rows])
    print(f"{name}: {len(rows)} mirrors, |sim-meas|/meas median {np.median(pct):.2f}%, 90% {np.quantile(pct, 0.9):.2f}%, max {pct.max():.2f}%; rnda median {np.median(rnda, axis=0).round(4).tolist()}")
if len(runs) == 2:
    (a, ra), (b, rb) = runs.items()
    shared = {int(r["mirror"]): r for r in rb}
    pairs = [(r, shared[int(r["mirror"])]) for r in ra if int(r["mirror"]) in shared]
    sa = np.array([p[0]["optimized_rnda"][0] for p in pairs]); sb = np.array([p[1]["optimized_rnda"][0] for p in pairs])
    print(f"{len(pairs)} shared mirrors: rnda sigma1 {a}/{b} mean ratio {np.mean(sa / sb):.3f}, spread {np.std(sa / sb):.3f}")
