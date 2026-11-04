"""Write the route telescope map and print the minimum safe input-plane height.

usage (container, PYTHONPATH=<worktree>/src): route_setup.py <telescope> <zenith_deg> <map.json> [seed=4242]
The input-plane height is the minimum safe height (simtools minimum_input_plane_height_m),
rounded up to 0.1 m. The radius is the model's telescope_sphere_radius.
Uses the run-context API of the simtools worktree (RunContext + OutputPaths, as shower_route.main).
"""
import json
import math
import os
import sys

from simtools import constants
from simtools.application.model_reader import create_model_reader
from simtools.io.output_paths import OutputPaths
from simtools.model.telescope_model import TelescopeModel
from simtools.ray_tracing.backends.interface import create_shower_tracer
from simtools.runtime.context import RunContext
from simtools.simtel.shower_photons import minimum_input_plane_height_m

tel, zen, out = sys.argv[1], float(sys.argv[2]), sys.argv[3]
seed = int(sys.argv[4]) if len(sys.argv) > 4 else 4242
work = "/workdir/external/obdeect-validation/phase3/work/setup"
context = RunContext.from_arguments({"output_path": work}, paths=OutputPaths(output_path=work))
reader = create_model_reader(simulation_models_path="/workdir/external/simulation-models")
SITE = os.environ.get("SITE", "South")
tm = TelescopeModel(site=SITE, telescope_name=tel, model_version="7.0.0",
                    model_reader=reader, context=context)
tracer = create_shower_tracer(tm, name=constants.SHOWER_PHOTON_RAY_TRACING_BACKEND)
radius = float(tm.get_parameter_value("telescope_sphere_radius"))
minimum = minimum_input_plane_height_m(tracer.optical_model(zen, seed), zen)
height = math.ceil(minimum * 10.0) / 10.0
entry = {"model": tel, "model_version": "7.0.0", "site": SITE, "dual_mirror": False,
         "radius_m": radius, "input_plane_height_m": height, "theta_deg": zen, "phi_deg": 0.0}
json.dump({"0": entry}, open(out, "w"), indent=1)  # IACT telescope id of the single-telescope file is 0
print(f"{tel} za {zen} radius {radius} min_height {minimum:.3f} used {height:.1f} map {out}", flush=True)
