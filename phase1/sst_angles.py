import os
import sys
import numpy as np
from simtools import settings
from simtools.application.model_reader import create_model_reader
from simtools.io import io_handler
from simtools.model.telescope_model import TelescopeModel
from simtools.ray_tracing.obdeect_backend import ObdeectRayTracer
if len(sys.argv) < 2:
    raise SystemExit("usage: sst_angles.py <sim_telarray photon-list.lis>")
f = sys.argv[1]
s = np.loadtxt(f, comments="#", usecols=(25, 28, 29, 31, 32, 33, 35))
s_focal, s_r1, s_a1, s_r2, s_a2 = s[:, 0], np.hypot(s[:, 1], s[:, 2]) / 100, s[:, 3], np.hypot(s[:, 4], s[:, 5]) / 100, s[:, 6]
settings.config.load(args={"output_path": "/tmp/sst"}, resolve_sim_software_executables=False)
io_handler.IOHandler().set_paths(output_path="/tmp/sst")
reader = create_model_reader(simulation_models_path=os.environ.get("MODELS_DIR", "/workdir/external/simulation-models"))
m = TelescopeModel(model_reader=reader, site="South", telescope_name="SSTS-01", model_version="6.0.2", label="sst")
a = ObdeectRayTracer(m, seed=8).trace_star(20.0, 1.0, 0.0, 1e4, 1_000_000)
d = a["detected"]
o_focal = np.degrees(np.arccos(np.abs(a["direction"][d, 2])))
o_r1 = np.hypot(*a["primary_point_m"][d, :2].T); o_a1 = a["primary_incidence_deg"][d]
o_r2 = np.hypot(*a["secondary_point_m"][d, :2].T); o_a2 = a["secondary_incidence_deg"][d]
print("detected sim", len(s_focal), "obdeect", d.sum())
print("primary radius range sim %.3f-%.3f obd %.3f-%.3f" % (s_r1.min(), s_r1.max(), o_r1.min(), o_r1.max()))
print("secondary radius range sim %.3f-%.3f obd %.3f-%.3f" % (s_r2.min(), s_r2.max(), o_r2.min(), o_r2.max()))
bins = np.linspace(0, 2.2, 12)
hs, _ = np.histogram(s_r1, bins); ho, _ = np.histogram(o_r1, bins)
print(" r1 bin    frac sim  frac obd | focal sim   obd  | sec. angle sim  obd")
for i in range(len(bins) - 1):
    ms = (s_r1 >= bins[i]) & (s_r1 < bins[i + 1]); mo = (o_r1 >= bins[i]) & (o_r1 < bins[i + 1])
    if ms.sum() < 10: continue
    print(f" {bins[i]:4.2f}-{bins[i+1]:4.2f} {hs[i]/len(s_r1):8.4f} {ho[i]/len(o_r1):8.4f} | {s_focal[ms].mean():7.3f} {o_focal[mo].mean():7.3f} | {s_a2[ms].mean():7.3f} {o_a2[mo].mean():7.3f}")
print("means focal %.3f %.3f  primary %.3f %.3f  secondary %.3f %.3f" % (s_focal.mean(), o_focal.mean(), s_a1.mean(), o_a1.mean(), s_a2.mean(), o_a2.mean()))
print("stat errors ~ %.3f" % (s_focal.std() / np.sqrt(len(s_focal)) * np.sqrt(2)))
