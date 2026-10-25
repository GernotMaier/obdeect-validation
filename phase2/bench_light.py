"""Single-core benchmark of calibration light: LightEmission (ff-1m, xyzls) and obdeect.

Usage: python bench_light.py <case> [core]

<case> is flasher (MSFx-FlashCam on MSTS-04, 100 pulses of 10^6 photons) or
illuminator (isotropic source 600 m above LSTN-01, 2 deg off axis, 10 pulses
of 10^9 photons). The LightEmission command is the one simtools ran in the
validation (read from its log); obdeect makes and traces the same source with
trace_emitter(threads=1) and simtools writes the photon bunches. Both stages
end with the photons sim_telarray reads; the sim_telarray camera stage after
them is the same for both and not timed here. Pinned to one core.
"""

import gzip
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import numpy as np

case = sys.argv[1]
core = int(sys.argv[2]) if len(sys.argv) > 2 else 3
os.sched_setaffinity(0, {core})

HERE = Path(__file__).resolve().parent
RUNS = Path(os.environ.get("RUNS_DIR", HERE / "runs"))
MODELS = Path(os.environ.get("MODELS_DIR", "/workdir/external/simulation-models")) / "simulation-models"
CASES = {
    "flasher": {
        "run": RUNS / "flasher-msts04-flashcam" / "sim_telarray-11",
        "telescope": "MSTS-04",
        "pulses": [1e6] * 100,
        "emitter": {
            # flasher_position (0.2, 0.2, -0.5) m in the primary-mirror frame.
            "intensity": ([0.0, 11.0, 11.0 * (1 + 1e-9)], [1.0, 1.0, 0.0]),
            "pulse": ([-1.25, 1.25], [1.0, 1.0]),
            "wavelength_nm": 385.0,
            "direct": True,
        },
        "flasher_xyz": (0.2, 0.2, -0.5),
        "camera_radius_m": 2.043538597629122,
    },
    "illuminator": {
        "run": RUNS / "illuminator-lstn01-offaxis" / "sim_telarray-11",
        "telescope": "LSTN-01",
        "pulses": [1e9] * 10,
        "emitter": {
            "position_m": (15.0, 15.0, 600.0),
            "axis": (0.0, 0.0, -1.0),
            "intensity": ([0.0, 180.0], [1.0, 1.0]),
            "wavelength_nm": 300.0,
        },
    },
}
setup = CASES[case]


def light_emission_seconds():
    log = next((setup["run"] / "sim_telarray").glob("*.light_emission.log.gz"))
    with gzip.open(log, "rt") as text:
        line = next(line for line in text if line.startswith("Program command line:"))
    command = line.split(":", 1)[1].split()
    with tempfile.TemporaryDirectory() as directory:
        output = Path(directory) / "photons.iact.gz"
        command[command.index("-o") + 1] = str(output)
        cwd = setup["run"] / "sim_telarray"
        start = time.perf_counter()
        subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                       cwd=cwd)
        seconds = time.perf_counter() - start
        size = output.stat().st_size
    return seconds, size, " ".join(command[:1])


def obdeect_seconds():
    from obdeect import OpticalModel  # pylint: disable=import-outside-toplevel

    from simtools.simtel.photon_bunch_file import camera_bunches, write_photon_bunches

    model = OpticalModel.from_simulation_models(
        MODELS, setup["telescope"], "7.0.0", configuration_seed=11, zenith_deg=0.0
    )
    emitter = dict(setup["emitter"])
    if case == "flasher":
        x, y, _ = setup["flasher_xyz"]
        plane = model.focal_surface_z_m
        # The flasher distance below the camera as in the ff-1m run (1650 cm).
        emitter["position_m"] = (x, y, plane - 16.5)
        emitter["disk"] = ((0.0, 0.0, plane), (0.0, 0.0, 1.0), setup["camera_radius_m"])
    totals = {"trace_s": 0.0, "photons": 0}

    def pulses():
        """Photon bunches pulse by pulse, as simtools writes them; tracing timed."""
        for pulse, emitted in enumerate(setup["pulses"]):
            start = time.perf_counter()
            blocks = list(
                model.trace_emitter_blocks(
                    emitted, seed=11, first_id=pulse << 40, threads=1, **emitter
                )
            )
            totals["trace_s"] += time.perf_counter() - start
            totals["photons"] += sum(len(b["weight"]) for b in blocks)
            yield np.concatenate(
                [camera_bunches(b, dual_mirror=False, emission_altitude_m=2147.0) for b in blocks]
            )

    with tempfile.TemporaryDirectory() as directory:
        start = time.perf_counter()
        write_photon_bunches(
            Path(directory) / "photons.iact.gz",
            pulses(),
            observation_level_m=2147.0,
            telescope_radius_m=10.0,
        )
        total_seconds = time.perf_counter() - start
    trace_seconds, photons = totals["trace_s"], totals["photons"]
    write_seconds = total_seconds - trace_seconds
    return trace_seconds, write_seconds, photons


light_seconds, light_bytes, program = light_emission_seconds()
trace_seconds, write_seconds, photons = obdeect_seconds()
result = {
    "case": case,
    "core": core,
    "photons_emitted": float(np.sum(setup["pulses"])),
    "light_emission_program": Path(program).name,
    "light_emission_s": light_seconds,
    "light_emission_output_bytes": light_bytes,
    "obdeect_trace_s": trace_seconds,
    "obdeect_photons_at_camera": photons,
    "bunch_file_write_s": write_seconds,
    "speedup_light_stage": light_seconds / (trace_seconds + write_seconds),
}
print(json.dumps(result, indent=1))
