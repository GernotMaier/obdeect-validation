"""
P7 follow-up: per-telescope acceptance tables for option B, including sim_telarray's instrument
path term (od2focus, sim_absorb.c:785, sim_telarray.c:1866-1868).

For each telescope of model 7.0.0 (LSTS-01, MSTS-04, LSTN-01, MSTN-07):
  transmission               sim_telarray lookup with ztel and pathlen_tel of that telescope
  transmission_atmosphere_only  same lookup with pathlen 0 (the table of build_acceptance_table.py)
Grid: 200-1000 nm (integer nm), emission altitude obs level and 3-30 km (1 km steps), zenith
0/20/40/60 deg. Every table value is also computed by the C harness (work/c_harness/harness) and
compared; the gate is max abs difference < 1e-3.

Also writes work/telescope_tables_<name>.json, including simtools (no path term) vs the port.

Run in the container:  python3 build_telescope_tables.py
"""

import json
import math
from pathlib import Path

import numpy as np
from astropy.table import Table

from build_acceptance_table import WAVELENGTHS_NM, ZENITHS_DEG
from check_port_against_c import HARNESS, OBS_M, VERSION, run_c
from simtel_transmission import SimtelTransmission
from telescope_parameters import TELESCOPES, telescope_parameters

HERE = Path(__file__).resolve().parent
GATE = 1e-3


def main():
    for name in TELESCOPES:
        tel = telescope_parameters(name)
        site = tel["site"]
        obs_m = OBS_M[site]
        grid = HERE / "work" / f"atmospheric_transmission-{site}-{VERSION[site]}.grid.dat"
        port = SimtelTransmission(grid, obs_m)
        heights_km = [obs_m / 1000.0] + [float(k) for k in range(3, 31)]

        rows = {"wavelength_nm": [], "emission_altitude_km": [], "zenith_deg": [],
                "airmass": [], "transmission": [], "transmission_atmosphere_only": []}
        cases = []
        for zen in ZENITHS_DEG:
            airmass = 1.0 / math.cos(math.radians(zen))
            for wl in WAVELENGTHS_NM:
                for zkm in heights_km:
                    rows["wavelength_nm"].append(int(wl))
                    rows["emission_altitude_km"].append(zkm)
                    rows["zenith_deg"].append(zen)
                    rows["airmass"].append(airmass)
                    cases.append((int(wl), zkm * 1000.0, airmass, tel["ztel_m"], tel["pathlen_m"]))
        values = np.array([port.transmission(w, z, t, a, p) for w, z, a, t, p in cases])
        atmo = np.array([port.transmission(w, z, t, a, 0.0) for w, z, a, t, p in cases])
        rows["transmission"] = values.tolist()
        rows["transmission_atmosphere_only"] = atmo.tolist()

        c_values = run_c(grid, obs_m, cases)
        table_diff = np.abs(c_values - values)
        i = int(np.argmax(table_diff))

        out = Table(rows)
        out["wavelength_nm"].unit = "nm"
        out["emission_altitude_km"].unit = "km"
        out["zenith_deg"].unit = "deg"
        out["transmission"].description = (
            "sim_telarray atmospheric_transmission2 incl. od2focus (telescope at ztel, pathlen_tel)")
        out["transmission_atmosphere_only"].description = "same with pathlen 0"
        out.meta.update({
            "telescope": name,
            "design_model": tel["design"],
            "site": site,
            "model_version": "7.0.0",
            "observatory_level_m": obs_m,
            "ztel_m": tel["ztel_m"],
            "pathlen_m": tel["pathlen_m"],
            "source": "sim_telarray sim_absorb.c atmospheric_transmission2 with od2tel/od2focus "
                      "from sim_telarray.c:1859-1868; table grid: simtools writer, opaque 99999 cells",
        })
        out.write(HERE / f"acceptance_telescope_{name.lower()}.ecsv", format="ascii.ecsv",
                  overwrite=True)

        summary = {
            "telescope": name,
            "ztel_m": tel["ztel_m"],
            "pathlen_m": tel["pathlen_m"],
            "n_table_cells": len(cases),
            "max_abs_diff_table_vs_c": float(table_diff.max()),
            "argmax_table_vs_c": {"wavelength_nm": cases[i][0], "emission_m": cases[i][1],
                                  "airmass": cases[i][2], "c": float(c_values[i]),
                                  "table": float(values[i])},
            "gate_1e-3": bool(table_diff.max() < GATE),
            "max_abs_path_term_effect": float(np.max(np.abs(values - atmo))),
        }
        (HERE / "work" / f"telescope_tables_{name.lower()}.json").write_text(
            json.dumps(summary, indent=2), encoding="utf-8")
        print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
