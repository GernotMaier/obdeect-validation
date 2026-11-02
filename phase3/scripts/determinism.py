"""Determinism of two route runs with the same seeds: sha256 of the files, and of the photo-electron content.
usage (container): determinism.py <point_dir> <tag_a> <tag_b>
The sim_telarray output file can differ in header metadata (times) while the photo-electron content is identical;
both are reported.
"""
import hashlib
import json
import sys

import numpy as np
from eventio import SimTelFile

point, a, b = sys.argv[1], sys.argv[2], sys.argv[3]


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def pe_content(path):
    h = hashlib.sha256()
    with SimTelFile(path) as f:
        for ev in f:
            h.update(str(int(ev["event_id"])).encode())
            for tel, d in sorted(ev.get("photoelectrons", {}).items()):
                if "pixel_id" in d:
                    h.update(np.asarray(d["pixel_id"]).tobytes())
                    h.update(np.asarray(d["time"], dtype=float).tobytes())
    return h.hexdigest()


out = {}
for name in ("bunches.iact", "route.simtel.zst"):
    ha = sha(f"{point}/route_{a}/{name}")
    hb = sha(f"{point}/route_{b}/{name}")
    out[name] = {"sha256_a": ha, "sha256_b": hb, "identical": ha == hb}
pa, pb = pe_content(f"{point}/route_{a}/route.simtel.zst"), pe_content(f"{point}/route_{b}/route.simtel.zst")
out["photoelectron_content_sha256"] = {"a": pa, "b": pb, "identical": pa == pb}
print(json.dumps(out, indent=1))
