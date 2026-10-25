"""Single-mirror mode with both backends: D80 per mirror panel."""
import sys
import os
import astropy.units as u
from simtools import settings
from simtools.application.model_reader import create_model_reader
from simtools.io import io_handler
from simtools.model.site_model import SiteModel
from simtools.model.telescope_model import TelescopeModel
from simtools.ray_tracing.ray_tracing import RayTracing

site, tel = sys.argv[1:3]
mirrors = [int(m) for m in sys.argv[3].split(",")]
models_dir = os.environ.get("MODELS_DIR", "/workdir/external/simulation-models")
out_dir = os.environ.get("OUT_DIR", "runs/single")
sim_telarray_dir = os.environ.get("SIM_TELARRAY_DIR", "/workdir/simulation_software/sim_telarray")
reader = create_model_reader(simulation_models_path=models_dir)
results = {}
for backend in ("sim_telarray", "obdeect"):
    out = f"{out_dir}/{tel}/{backend}"
    settings.config.load(args={"output_path": out, "ray_tracing_backend": backend, "obdeect_seed": 4,
                               "sim_telarray_path": sim_telarray_dir})
    io_handler.IOHandler().set_paths(output_path=out)
    model = TelescopeModel(model_reader=reader, site=site, telescope_name=tel, model_version="6.0.2", label="single")
    model.export_model_files()
    site_model = SiteModel(model_reader=reader, site=site, model_version="6.0.2", label="single")
    rt = RayTracing(model, site_model, label="single", zenith_angle=0 * u.deg, source_distance=10 * u.km,
                    single_mirror_mode=True, mirror_numbers=mirrors, off_axis_angle=[0] * u.deg)
    rt.simulate(test=False, force=True)
    rt.analyze(force=True, export=False)
    results[backend] = [(int(r["mirror_number"]), float(r["psf_cm"].value), float(r["eff_area"].value)) for r in rt._results]
for (m, ps, As), (_, po, Ao) in zip(results["sim_telarray"], results["obdeect"]):
    print(f"mirror {m:3d} d80 cm {ps:7.3f} {po:7.3f} ratio {po/ps:6.3f}   area {As:7.4f} {Ao:7.4f}")
import numpy as np
for b in results:
    d = np.array([r[1] for r in results[b]])
    print(f"{b:13s} mean d80 {d.mean():.3f} cm  std {d.std(ddof=1):.3f}  n {len(d)}")
