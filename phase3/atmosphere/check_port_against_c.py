"""
P7 step 3 (per telescope): check the Python port, including the od2focus path term, against
sim_telarray's C code.

The C side is work/c_harness/harness, built from the unmodified RT/sim_telarray/common/sim_absorb.c
and rpolator.c. Its driver computes the telescope optical depths exactly as sim_telarray.c:1859-1868
does (ztel, pathlen) and calls atmospheric_transmission2 (sim_telarray.c:2861).

Per telescope: 20 000 random (wavelength, emission altitude, zenith) cases, with ztel and pathlen
of that telescope (telescope_parameters.py). Gate: max abs difference < 1e-3.

Run in the container:  python3 check_port_against_c.py
"""

import math
import subprocess
from pathlib import Path

import numpy as np

from simtel_transmission import SimtelTransmission
from telescope_parameters import TELESCOPES, telescope_parameters

HERE = Path(__file__).resolve().parent
HARNESS = HERE / "work" / "c_harness" / "harness"
OBS_M = {"South": 2147.0, "North": 2156.0}
VERSION = {"South": "1.0.0", "North": "2.0.0"}
GATE = 1e-3


def run_c(grid, obs_m, cases):
    """cases: list of (iwl, zem_m, airmass, ztel_m, pathlen_m). Returns C transmissions."""
    stdin = "\n".join(
        f"{int(w)} {z * 100.0:.17g} {a:.17g} {t * 100.0:.17g} {p * 100.0:.17g}"
        for w, z, a, t, p in cases
    )
    out = subprocess.run([str(HARNESS), str(grid), str(obs_m)], input=stdin,
                         capture_output=True, text=True, check=True).stdout.split()
    return np.array([float(v) for v in out])


def main():
    rng = np.random.default_rng(7)
    n = 20000
    summary = {}
    for name in TELESCOPES:
        tel = telescope_parameters(name)
        site = tel["site"]
        obs_m = OBS_M[site]
        grid = HERE / "work" / f"atmospheric_transmission-{site}-{VERSION[site]}.grid.dat"
        wl = rng.integers(200, 1001, n)
        zem_m = np.concatenate([rng.uniform(obs_m, 30000.0, n // 2),
                                rng.uniform(obs_m - 500.0, obs_m + 100.0, n // 2)])
        airmass = 1.0 / np.cos(np.radians(rng.choice([0.0, 20.0, 40.0, 60.0, 30.0, 75.0], n)))
        cases = [(int(w), float(z), float(a), tel["ztel_m"], tel["pathlen_m"])
                 for w, z, a in zip(wl, zem_m, airmass)]
        c_values = run_c(grid, obs_m, cases)
        port = SimtelTransmission(grid, obs_m)
        py_values = np.array([port.transmission(w, z, t, a, p) for w, z, a, t, p in cases])
        diff = np.abs(c_values - py_values)
        i = int(np.argmax(diff))
        summary[name] = {
            "ztel_m": tel["ztel_m"],
            "pathlen_m": tel["pathlen_m"],
            "n_cases": n,
            "max_abs_diff_port_vs_c": float(diff.max()),
            "n_nonzero_c": int(np.sum(c_values > 0)),
            "gate_1e-3": bool(diff.max() < GATE),
            "argmax": {"wavelength_nm": cases[i][0], "emission_m": cases[i][1],
                       "airmass": cases[i][2], "c": float(c_values[i]),
                       "port": float(py_values[i])},
        }
        print(name, summary[name])
    return summary


if __name__ == "__main__":
    main()
