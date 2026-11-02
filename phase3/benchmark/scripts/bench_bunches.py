"""trace_bunches against trace(detected_only=True) on the same star photons (best of three).

usage: bench_bunches.py <model.json> <photons> <threads> [acceptance]
The star photons become bunches of size 1 (identity frame, unit 1, wavelength 400 nm,
constant acceptance, default 0.2). Reports ns per input bunch and per output photon.
Run with PYTHONPATH set to the obdeect build under test.
"""

import sys
import time

import numpy as np
from obdeect import OpticalModel, ThreadPool

model = OpticalModel.load(sys.argv[1])
n, threads = int(sys.argv[2]), int(sys.argv[3])
acceptance_value = float(sys.argv[4]) if len(sys.argv) > 4 else 0.2
wavelength_nm = 400.0

photons = model.star_photons(n, seed=3, wavelength_nm=wavelength_nm, distance_m=1e4)
plane_z = float(photons["position_m"][0, 2])
x, y, z = photons["position_m"].T
bunches = {
    "x": x.astype(np.float32),
    "y": y.astype(np.float32),
    "cx": photons["direction"][:, 0].astype(np.float32),
    "cy": photons["direction"][:, 1].astype(np.float32),
    "time_ns": photons["time_ns"].astype(np.float32),
    "zem": np.full(n, 10_000.0, dtype=np.float32),
    "size": np.ones(n, dtype=np.float32),
    "wavelength_nm": np.full(n, wavelength_nm, dtype=np.float32),
    "bunch_id": np.arange(n, dtype=np.uint64),
}
acceptance = (
    np.array([100.0, 1000.0]),
    np.array([0.0, 1.0e6]),
    np.full((2, 2), acceptance_value),
)
pool = ThreadPool(threads)
outputs = ["position_m", "direction", "time_ns", "weight"]


def best_of_three(function):
    best = 1e9
    for _ in range(3):
        start = time.perf_counter()
        result = function()
        best = min(best, time.perf_counter() - start)
    return best, result


t_trace, traced = best_of_three(
    lambda: model.trace(
        photons, seed=3, detected_only=True, outputs=outputs, pool=pool
    )
)
t_bunch, out = best_of_three(
    lambda: model.trace_bunches(
        bunches,
        seed=3,
        frame_rotation=np.eye(3),
        frame_offset_m=(0.0, 0.0, 0.0),
        length_unit_m=1.0,
        plane_z=plane_z,
        acceptance=acceptance,
        pool=pool,
    )
)
detected = len(traced["weight"])
kept = len(out["weight"])
ns_trace = 1e9 * t_trace / n
ns_bunch = 1e9 * t_bunch / n
print(f"trace(detected_only)  {ns_trace:8.1f} ns per photon   ({detected} detected)")
print(
    f"trace_bunches         {ns_bunch:8.1f} ns per input bunch   "
    f"{1e9 * t_bunch / max(kept, 1):8.1f} ns per output photon   ({kept} kept)"
)
print(f"ratio bunch / trace   {ns_bunch / ns_trace:6.3f}   threads={threads} acceptance={acceptance_value}")
