"""Per-mirror hit fractions: sim_telarray photon list vs obdeect (MSTN-01 6.0.2, on axis)."""
import gzip, sys, os
import numpy as np
from simtools.application.model_reader import create_model_reader
from simtools import settings
from simtools.io import io_handler
from simtools.model.telescope_model import TelescopeModel
from simtools.ray_tracing.obdeect_backend import ObdeectRayTracer

if len(sys.argv) < 2:
    raise SystemExit("usage: permirror.py <sim_telarray photon-list.lis.gz>")
f = sys.argv[1]
rows, total = [], 0
for line in gzip.open(f, "rt"):
    if "falling on an area" in line:
        total += int(line.split()[4]); area = float(line.split()[14])
    if line.startswith("#") or not line.strip():
        continue
    w = line.split(); rows.append((float(w[4]), float(w[5]), float(w[6]), int(w[8])))
s = np.array(rows)
print("sim_telarray", total, len(s), len(s) / total * area, "z0", np.unique(s[:, 2])[:3])

settings.config.load(args={"output_path": "/tmp/pm"}, resolve_sim_software_executables=False)
io_handler.IOHandler().set_paths(output_path="/tmp/pm")
reader = create_model_reader(simulation_models_path=os.environ.get("MODELS_DIR", "/workdir/external/simulation-models"))
m = TelescopeModel(model_reader=reader, site="North", telescope_name="MSTN-01", model_version="6.0.2", label="pm")
tr = ObdeectRayTracer(m, seed=21)
N = 3_000_000
a = tr.trace_star(20.0, 0.0, 0.0, 1e4, N, 20)
d = a["detected"]
print("obdeect", N, d.sum(), d.sum() / N * a["total_area_m2"], a["total_area_m2"])
ids_s, cs = np.unique(s[:, 3].astype(int), return_counts=True)
ids_o, co = np.unique(a["primary_surface"][d], return_counts=True)
print("mirror ids sim", ids_s[:3], ids_s[-3:], "obdeect", ids_o[:3], ids_o[-3:])
fs = dict(zip(ids_s, cs / total)); fo = dict(zip(ids_o, co / N))
diff = np.array([(k, fs.get(k, 0), fo.get(k, 0)) for k in sorted(set(fs) | set(fo))])
rel = (diff[:, 2] - diff[:, 1]) / np.sqrt(diff[:, 1] / total + diff[:, 2] / N)
print("per-mirror pulls: mean %.2f std %.2f min %.2f max %.2f" % (rel.mean(), rel.std(), rel.min(), rel.max()))
worst = np.argsort(-np.abs(rel))[:6]
facets = tr.optical_model(20.0, 0).document["optics"]["primary"]["facets"]
for i in worst:
    k = int(diff[i, 0]); fc = facets[k]
    print(f"mirror {k}: sim {diff[i,1]*1e4:.2f} obd {diff[i,2]*1e4:.2f} (1e-4) pull {rel[i]:.1f} centre {np.round(fc['centre_m'],2)} shape {fc['shape']}")
# Radial distribution of start positions (detected), sim vs obdeect.
# obdeect start positions: trace back from primary point along the incoming direction to z = disk.
