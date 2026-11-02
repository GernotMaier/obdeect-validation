"""
P7 follow-up: test of the proposed simtools change (work/simtools_proposal/transmission_patched.py,
NOT applied to simtools) against the sim_telarray port incl. the path term.

Wavelengths 291-1000 nm (complete grid rows, no opaque 99999 cells) and emission 0 to 30 km.
Also reports the unpatched simtools value to show the size of the missing term.
"""

import importlib.util
import math
from pathlib import Path

import numpy as np
from astropy.table import Table

from simtel_transmission import SimtelTransmission
from telescope_parameters import MODELS, TELESCOPES, telescope_parameters

HERE = Path(__file__).resolve().parent
PATCHED = HERE / "work" / "simtools_proposal" / "transmission_patched.py"
ORIGINAL = HERE / "work" / "simtools_proposal" / "transmission_orig.py"
OBS = {"South": ("OBS-South", "1.0.0", 2147.0), "North": ("OBS-North", "2.0.0", 2156.0)}


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    rng = np.random.default_rng(11)
    patched_mod = load(PATCHED, "transmission_patched")
    orig_mod = load(ORIGINAL, "transmission_orig")
    for name in TELESCOPES:
        tel = telescope_parameters(name)
        instrument, version, obs = OBS[tel["site"]]
        table = Table.read(MODELS / instrument / "atmospheric_transmission" /
                           f"atmospheric_transmission-{version}.ecsv")
        patched = patched_mod.AtmosphericTransmission(table)
        orig = orig_mod.AtmosphericTransmission(table)
        port = SimtelTransmission(HERE / "work" / f"atmospheric_transmission-{tel['site']}-{version}.grid.dat", obs)
        worst_patched = worst_orig = 0.0
        for _ in range(3000):
            wl = int(rng.integers(291, 1001))
            zem = float(rng.uniform(obs, 30000.0))
            airmass = 1.0 / math.cos(math.radians(float(rng.choice([0.0, 20.0, 40.0, 60.0]))))
            ref = port.transmission(wl, zem, tel["ztel_m"], airmass, tel["pathlen_m"])
            new = float(patched.transmission(float(wl), zem, obs + tel["ztel_m"], airmass,
                                             tel["pathlen_m"]))
            old = float(orig.transmission(float(wl), zem, obs + tel["ztel_m"], airmass))
            worst_patched = max(worst_patched, abs(new - ref))
            worst_orig = max(worst_orig, abs(old - ref))
        print(name, "patched simtools vs port incl path (291-1000 nm):", worst_patched,
              "| unpatched simtools vs port:", worst_orig)


if __name__ == "__main__":
    main()
