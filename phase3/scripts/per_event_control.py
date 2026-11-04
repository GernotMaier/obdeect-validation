"""R8 control: per-event arrival-time scatter of native seed pairs (same method as per_event_times.py).

usage (container): per_event_control.py <point_dir> <seed_a> <seed_b>
Per matched event: mean p.e. time of native seed a minus native seed b. Prints N, mean, SD, SEM, count |dt| > 0.2 ns.
"""
import json
import math
import sys
import warnings

import numpy as np
from eventio import SimTelFile

warnings.filterwarnings("ignore")


def mean_times(path):
    out = {}
    with SimTelFile(path) as f:
        for ev in f:
            ts = [np.asarray(d["time"], dtype=float) for _t, d in ev.get("photoelectrons", {}).items()
                  if "time" in d and len(d["time"])]
            if ts:
                out[int(ev["event_id"])] = float(np.concatenate(ts).mean())
    return out


point, sa, sb = sys.argv[1], sys.argv[2], sys.argv[3]
a = mean_times(f"{point}/native_s{sa}/native.simtel.zst")
b = mean_times(f"{point}/native_s{sb}/native.simtel.zst")
common = sorted(set(a) & set(b))
dt = np.array([a[e] - b[e] for e in common])
print(json.dumps({"point": point, "seeds": [sa, sb], "n_matched_events": int(dt.size),
                  "mean_dt_ns": float(dt.mean()), "sd_dt_ns": float(dt.std(ddof=1)),
                  "sem_dt_ns": float(dt.std(ddof=1) / math.sqrt(dt.size)),
                  "n_abs_dt_gt_0p2ns": int((np.abs(dt) > 0.2).sum())}, indent=1))
