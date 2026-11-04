"""R8: per-event arrival-time comparison, route vs native (one native seed as reference).

usage (container): per_event_times.py <point_dir> <route_tag> <native_seed>
Per event (sim_telarray event_id, matched in both files, with photo-electrons in both): mean p.e. arrival time
of the route minus that of native. Reports N, mean, SD, SEM, median, min/max, and the count of events with
|dt| > 0.2 ns. Also prints the per-event list as JSON lines when PER_EVENT=1.
"""
import json
import math
import os
import sys
import warnings

import numpy as np
from eventio import SimTelFile
from scipy import stats

warnings.filterwarnings("ignore")


def mean_times(path):
    out = {}
    with SimTelFile(path) as f:
        for ev in f:
            ts = [np.asarray(d["time"], dtype=float) for _t, d in ev.get("photoelectrons", {}).items()
                  if "time" in d and len(d["time"])]
            if ts:
                allt = np.concatenate(ts)
                out[int(ev["event_id"])] = (float(allt.mean()), allt)
    return out


point, tag, seed = sys.argv[1], sys.argv[2], sys.argv[3]
r = mean_times(f"{point}/route_{tag}/route.simtel.zst")
n = mean_times(f"{point}/native_s{seed}/native.simtel.zst")
common = sorted(set(r) & set(n))
dt = np.array([r[e][0] - n[e][0] for e in common])
ks = stats.ks_2samp(np.concatenate([r[e][1] for e in common]), np.concatenate([n[e][1] for e in common]))
res = {"point": point, "route_tag": tag, "native_seed": seed, "n_matched_events": int(dt.size),
       "mean_dt_ns": float(dt.mean()), "sd_dt_ns": float(dt.std(ddof=1)),
       "sem_dt_ns": float(dt.std(ddof=1) / math.sqrt(dt.size)), "median_dt_ns": float(np.median(dt)),
       "min_dt_ns": float(dt.min()), "max_dt_ns": float(dt.max()),
       "n_abs_dt_gt_0p2ns": int((np.abs(dt) > 0.2).sum()),
       "ks_pooled_pe_D": float(ks.statistic), "ks_pooled_pe_p": float(ks.pvalue)}
print(json.dumps(res, indent=1))
if os.environ.get("PER_EVENT") == "1":
    for e, d in zip(common, dt):
        print(json.dumps({"event_id": e, "dt_ns": float(d)}))
