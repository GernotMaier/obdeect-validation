"""Single-core benchmark of star-light ray tracing: sim_telarray and obdeect, same photons.

Usage: python bench_star.py <telescope> <sim_telarray model directory> [core]

Both codes run pinned to one CPU core (sched_setaffinity / taskset), the same
telescope model (simulation models 7.0.0), zenith 20 deg, a star on axis at
10 km and the same numbers of photons sampled on the telescope entrance disk.
Per-photon costs are the slope between two photon numbers, which removes
start-up (configuration, mirror setup, model compilation), best of three runs.

- sim_telarray: the star-light mode simtools uses for ray tracing (options of
  SimulatorRayTracing.make_run_command), once writing the imaging list as
  simtools does, once without it.
- obdeect: star_photons + trace(threads=1), geometry only (as simtools) and
  with responses (reflectivity, transmission).
"""

import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

N1, N2, REPEAT = 200_000, 2_000_000, 3
SIM_TELARRAY = Path(os.environ.get("SIM_TELARRAY_DIR", "/workdir/simulation_software/sim_telarray"))
MODELS = Path(os.environ.get("MODELS_DIR", "/workdir/external/simulation-models")) / "simulation-models"
telescope, model_dir = sys.argv[1], Path(sys.argv[2]).resolve()
core = int(sys.argv[3]) if len(sys.argv) > 3 else 3
os.sched_setaffinity(0, {core})  # Before obdeect creates threads; children inherit it.


def best(function):
    """Minimum wall time of REPEAT calls [s]."""
    times = []
    for _ in range(REPEAT):
        start = time.perf_counter()
        function()
        times.append(time.perf_counter() - start)
    return min(times)


def sim_telarray_run(photons, imaging_list, work):
    stars = work / "stars.lis"
    stars.write_text("0. 70.0 1.0 10.0\n", encoding="utf-8")
    options = {
        "random_state": "none",
        "stars": str(stars),
        "altitude": "2156",
        "telescope_theta": "20.0",
        "telescope_phi": "0.0",
        "star_photons": str(photons),
        "camera_transmission": "1.0",
        "nightsky_background": "all:0.",
        "trigger_current_limit": "1e10",
        "telescope_random_angle": "0",
        "telescope_random_error": "0",
        "convergent_depth": "0",
        "maximum_telescopes": "1",
        "show": "all",
        "camera_filter": "none",
        "random_seed": "11,111",
        "output_file": "/dev/null",
    }
    if imaging_list:
        options["IMAGING_LIST"] = str(work / "photons.lis")
    command = [
        str(SIM_TELARRAY / "bin" / "sim_telarray"),
        "-c",
        str(next(model_dir.glob(f"CTAO-{telescope}.cfg"))),
        f"-I{model_dir}",
    ]
    for key, value in options.items():
        command += ["-C", f"{key}={value}"]
    command.append(str(SIM_TELARRAY / "run9991.corsika.gz"))
    environment = os.environ | {"SIM_TELARRAY_CONFIG_PATH": ""}

    def run():
        subprocess.run(
            command, env=environment, check=True, stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL, cwd=work,
        )

    return run


def obdeect_costs():
    from obdeect import OpticalModel  # pylint: disable=import-outside-toplevel

    start = time.perf_counter()
    model = OpticalModel.from_simulation_models(
        MODELS, telescope, "7.0.0", configuration_seed=11, zenith_deg=20.0
    )
    compile_s = time.perf_counter() - start
    result = {"compile_s": compile_s}
    for responses in (False, True):
        sample, trace = {}, {}
        for n in (N1, N2):
            photons = model.star_photons(n, seed=3, distance_m=1e4)
            sample[n] = best(lambda n=n: model.star_photons(n, seed=3, distance_m=1e4))
            trace[n] = best(
                lambda p=photons: model.trace(p, seed=3, apply_responses=responses, threads=1)
            )
        key = "responses" if responses else "geometry"
        result[f"obdeect_{key}_us"] = 1e6 * (
            (sample[N2] + trace[N2]) - (sample[N1] + trace[N1])
        ) / (N2 - N1)
        result[f"obdeect_{key}_trace_only_us"] = 1e6 * (trace[N2] - trace[N1]) / (N2 - N1)
    result["obdeect_structure"] = model.has_structure
    return result


result = {"telescope": telescope, "core": core, "photons": [N1, N2]}
with tempfile.TemporaryDirectory() as directory:
    work = Path(directory)
    for imaging_list in (True, False):
        times = {n: best(sim_telarray_run(n, imaging_list, work)) for n in (N1, N2)}
        key = "sim_telarray_list_us" if imaging_list else "sim_telarray_no_list_us"
        result[key] = 1e6 * (times[N2] - times[N1]) / (N2 - N1)
        result[key.replace("_us", "_startup_s")] = times[N1] - N1 * result[key] * 1e-6
result |= obdeect_costs()
result["speedup_simtools_mode"] = result["sim_telarray_list_us"] / result["obdeect_geometry_us"]
result["speedup_no_list"] = result["sim_telarray_no_list_us"] / result["obdeect_geometry_us"]
print(json.dumps(result, indent=1))
