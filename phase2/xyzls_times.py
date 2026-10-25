"""Bunch times of an xyzls file against the straight-line flight time from the source.

Usage: python xyzls_times.py <case run directory> [photons]

Re-runs the xyzls command of the run (fewer photons) and compares, per bunch,
the time with |source - bunch point| / c (bunch point: x, y at the horizontal
plane through the telescope sphere centre, z = telescope z of the run). The
time origin is free: the spread of the difference is what matters.
"""

import gzip
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from eventio import IACTFile

run = Path(sys.argv[1])
photons = sys.argv[2] if len(sys.argv) > 2 else "100000000"
log = next((run / "sim_telarray").glob("*.light_emission.log.gz"))
with gzip.open(log, "rt") as text:
    command = next(l for l in text if l.startswith("Program command line:")).split(":", 1)[1].split()
value = {command[i]: command[i + 1] for i in range(len(command) - 1) if command[i].startswith("-")}
source = np.array([float(value["-x"]), float(value["-y"]), float(value["-z"])])  # cm
telescope = np.array([float(v) for v in (run / "light_emission").glob("*.dat").__next__()
                      .read_text().split()[:3]])  # cm, x y z
with tempfile.TemporaryDirectory() as directory:
    output = Path(directory) / "x.iact"
    command[command.index("-o") + 1] = str(output)
    command[command.index("-n") + 1] = photons
    command[command.index("-N") + 1] = "1"
    subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                   cwd=directory)
    with IACTFile(str(output)) as f:
        event = next(iter(f))
        bunches = event.photon_bunches[0]
print("bunches", len(bunches), "source (m)", source / 100, "telescope (m)", telescope / 100)
# Bunch point relative to the telescope, at the plane through the sphere centre (z = 0).
point = np.column_stack([bunches["x"], bunches["y"], np.zeros(len(bunches))]) + telescope
point[:, 2] = telescope[2]
distance = np.linalg.norm(point - source, axis=1)  # cm
straight = distance / 29.9792458  # ns
difference = bunches["time"] - straight
difference -= np.median(difference)
print("bunch time - straight flight [ns]: rms %.3f, quantiles 1,5,50,95,99%%:" % difference.std(),
      np.percentile(difference, [1, 5, 50, 95, 99]).round(3))
radius = np.hypot(bunches["x"], bunches["y"]) / 100
for low, high in ((0, 20), (20, 50), (50, 100), (100, 200), (200, 1000)):
    selected = (radius >= low) & (radius < high)
    if selected.sum() > 10:
        print(f"  bunch point {low:4d}-{high:4d} m from the telescope: {selected.sum():7d} bunches,"
              f" mean difference {difference[selected].mean():7.3f} ns")
