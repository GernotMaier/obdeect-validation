"""P7 extra check: telescope-altitude term of simtools vs the sim_telarray port (pathlen 0)."""

import math
from pathlib import Path

import numpy as np
from astropy.table import Table

from simtools.atmosphere.transmission import AtmosphericTransmission
from simtel_transmission import SimtelTransmission

HERE = Path(__file__).resolve().parent
TELESCOPE_HEIGHTS_M = [0.0, 10.0, 50.0, 100.0]  # realistic heights above the observatory
MODELS = Path("/workdir/external/simulation-models/simulation-models/model_parameters")


def main():
    rng = np.random.default_rng(3)
    print("telescope heights [m]:", TELESCOPE_HEIGHTS_M)
    for site, version, obs in [("South", "1.0.0", 2147.0), ("North", "2.0.0", 2156.0)]:
        table = Table.read(MODELS / f"OBS-{site}" / "atmospheric_transmission" /
                           f"atmospheric_transmission-{version}.ecsv")
        tools = AtmosphericTransmission(table)
        port = SimtelTransmission(HERE / "work" / f"atmospheric_transmission-{site}-{version}.grid.dat", obs)
        worst, case = 0.0, None
        for _ in range(3000):
            wl = int(rng.integers(200, 1001))
            zem = float(rng.uniform(obs, 30000.0))
            ztel = float(rng.choice(TELESCOPE_HEIGHTS_M))
            airmass = 1.0 / math.cos(math.radians(float(rng.choice([0.0, 20.0, 40.0, 60.0]))))
            a = port.transmission(wl, zem, ztel, airmass, 0.0)
            b = float(tools.transmission(float(wl), zem, obs + ztel, airmass))
            if abs(a - b) > worst:
                worst, case = abs(a - b), (wl, round(zem), ztel, round(airmass, 3), a, b)
        print(site, "max |port - simtools| with telescope altitude, pathlen 0:", worst, case)


if __name__ == "__main__":
    main()
