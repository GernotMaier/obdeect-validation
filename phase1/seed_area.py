"""Effective area of obdeect for several seeds (geometry only, on axis, 2e6 photons)."""
import sys
import os
from simtools.application.model_reader import create_model_reader
from simtools import settings
from simtools.model.telescope_model import TelescopeModel
from simtools.ray_tracing.obdeect_backend import ObdeectRayTracer

settings.config.load(args={"output_path": "/tmp/seedarea"}, resolve_sim_software_executables=False)
reader = create_model_reader(simulation_models_path=os.environ.get("MODELS_DIR", "/workdir/external/simulation-models"))
site, tel, version = sys.argv[1:4]
from simtools.io import io_handler
io_handler.IOHandler().set_paths(output_path="/tmp/seedarea")
model = TelescopeModel(model_reader=reader, site=site, telescope_name=tel, model_version=version, label="seed")
for seed in range(1, 9):
    a = ObdeectRayTracer(model, seed=seed).trace_star(20.0, 0.0, 0.0, 1.0e4, 2_000_000, 20)
    print(seed, a["detected"].sum() / a["total_photons"] * a["total_area_m2"])
