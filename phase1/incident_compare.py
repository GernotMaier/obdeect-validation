import glob, os, sys
import numpy as np
from astropy.table import QTable
import os
tag = os.environ.get("TAG", "")
out_dir = os.environ.get("OUT_DIR", "runs/incident" + tag)
for tel in sys.argv[1:]:
    print(tel)
    for f in sorted(glob.glob(f"{out_dir}/{tel}/obdeect/{tel}/*.ecsv")):
        name = f.split("/")[-1]
        rows = []
        for b in ("sim_telarray", "obdeect"):
            t = QTable.read(f.replace("/obdeect/", f"/{b}/", 1))
            a, w = (np.asarray(t[c].value if hasattr(t[c], "value") else t[c], float) for c in t.colnames[:2])
            w = w / w.sum(); c = np.cumsum(w)
            q = [a[np.searchsorted(c, p)] for p in (0.1, 0.5, 0.9)]
            rows.append((a @ w, q))
        (ms, qs), (mo, qo) = rows
        print(f"  {name:42s} mean {ms:7.3f} {mo:7.3f} | q10/50/90 sim {np.round(qs,2)} obd {np.round(qo,2)}")
