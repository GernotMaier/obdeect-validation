"""
P7: compare simtools' atmospheric transmission with sim_telarray's and build the
option-B acceptance table (wavelength, emission altitude, airmass -> transmission).

Run inside the obdeect-val container (simtools editable from RT/simtools):

    python3 build_acceptance_table.py <site: South|North>

Steps
1. Export the model-7.0.0 table with simtools' own sim_telarray writer
   (the file sim_telarray reads, incl. the 99999 opaque cells).
2. sim_telarray side: simtel_transmission.py (port of sim_absorb.c).
3. simtools side: simtools.atmosphere.transmission.AtmosphericTransmission on the ECSV.
4. Compare over 200-1000 nm (integer nm), emission altitude obs level..30 km,
   zenith 0/20/40/60 deg, telescope at observation level (no instrument term).
5. Write the acceptance table (sim_telarray values) and a JSON summary.
"""

import json
import math
import sys
from pathlib import Path

import astropy.units as u
import numpy as np
from astropy.table import Table

from simtools.atmosphere.transmission import AtmosphericTransmission
from simtools.data_model import schema
from simtools.data_model.table_asset import get_simtel_serialization
from simtools.simtel import table_serializers
from simtel_transmission import SimtelTransmission

HERE = Path(__file__).resolve().parent
MODELS = Path("/workdir/external/simulation-models/simulation-models/model_parameters")
SITES = {"South": ("OBS-South", "1.0.0"), "North": ("OBS-North", "2.0.0")}
ZENITHS_DEG = [0.0, 20.0, 40.0, 60.0]
WAVELENGTHS_NM = np.arange(200, 1001)


def export_grid(site, table, work_dir):
    """Write the sim_telarray grid file with simtools' writer and its schema contract."""
    instrument, version = SITES[site]
    param = json.loads((MODELS / SITES[site][0] / "atmospheric_transmission" /
                        f"atmospheric_transmission-{version}.json").read_text(encoding="utf-8"))
    schema_data = schema.get_model_parameter_schema(
        "atmospheric_transmission", param["model_parameter_schema_version"]
    )
    contract = get_simtel_serialization(schema_data)
    contract["table_format"] = "atmospheric_transmission"
    name = f"atmospheric_transmission-{site}-{version}.grid.dat"
    table_serializers.write_simtel_table(table, work_dir, contract=contract, output_name=name)
    return work_dir / name


def main(site):
    instrument, version = SITES[site]
    work = HERE / "work"
    work.mkdir(exist_ok=True)
    table = Table.read(MODELS / instrument / "atmospheric_transmission" /
                       f"atmospheric_transmission-{version}.ecsv")
    obs_m = u.Quantity(table.meta["observatory_level"]).to_value(u.m)
    grid = export_grid(site, table, work)
    sim = SimtelTransmission(grid, obs_m)
    simtools_model = AtmosphericTransmission(table)

    emission_m = np.unique(np.concatenate([
        np.arange(obs_m, 30000.0 + 1e-6, 100.0),
        np.array(table["altitude"], float)[np.array(table["altitude"], float) * 1000 <= 30000]
        * 1000.0,
    ]))
    emission_m = emission_m[emission_m >= obs_m]

    diffs = np.zeros((len(ZENITHS_DEG), len(WAVELENGTHS_NM), len(emission_m)))
    sim_vals = np.zeros_like(diffs)
    tools_vals = np.zeros_like(diffs)
    for iz, zen in enumerate(ZENITHS_DEG):
        airmass = 1.0 / math.cos(math.radians(zen))
        for iw, wl in enumerate(WAVELENGTHS_NM):
            tools = simtools_model.transmission(float(wl), emission_m, obs_m, airmass)
            for ie, zem in enumerate(emission_m):
                sim_vals[iz, iw, ie] = sim.transmission(wl, zem, 0.0, airmass)
            tools_vals[iz, iw, :] = tools
    diffs = np.abs(sim_vals - tools_vals)
    iz, iw, ie = np.unravel_index(np.argmax(diffs), diffs.shape)
    max_diff = dict(
        value=float(diffs[iz, iw, ie]),
        zenith_deg=ZENITHS_DEG[iz],
        wavelength_nm=int(WAVELENGTHS_NM[iw]),
        emission_altitude_km=float(emission_m[ie] / 1000.0),
        sim_telarray=float(sim_vals[iz, iw, ie]),
        simtools=float(tools_vals[iz, iw, ie]),
    )
    # Wavelengths with a complete altitude grid in the ECSV (no 99999 cells in the export).
    wl_table = np.array(table["wavelength"], float)
    complete = np.array([np.sum(wl_table == wl) == 40 for wl in WAVELENGTHS_NM])
    summary = {
        "site": site,
        "table": f"{instrument}/atmospheric_transmission-{version}",
        "observatory_level_m": obs_m,
        "n_cells": int(diffs.size),
        "max_abs_diff": max_diff,
        "n_cells_above_0p1_percent": int(np.sum(diffs >= 1e-3)),
        "max_abs_diff_complete_wavelengths": float(diffs[:, complete, :].max()),
        "max_abs_diff_incomplete_wavelengths": float(diffs[:, ~complete, :].max()),
        "n_incomplete_wavelengths": int(np.sum(~complete)),
        "n_cells_sim_zero_simtools_above_1e-3": int(np.sum((sim_vals == 0) & (tools_vals > 1e-3))),
        "max_abs_diff_where_simtools_above_1e-2": float(
            np.max(np.where(tools_vals > 1e-2, diffs, 0.0))
        ),
        "max_rel_diff_where_simtools_above_1e-2": float(
            np.max(np.where(tools_vals > 1e-2, diffs / np.maximum(tools_vals, 1e-300), 0.0))
        ),
    }
    json.dump(summary, open(work / f"compare_{site}.json", "w"), indent=2)
    print(json.dumps(summary, indent=2))

    # Acceptance table: sim_telarray values, telescope at observation level, 1 km heights.
    acc_km = [obs_m / 1000.0] + [float(k) for k in range(3, 31)]
    rows = {"wavelength_nm": [], "emission_altitude_km": [], "zenith_deg": [], "airmass": [],
            "transmission": [], "transmission_simtools": []}
    for zen in ZENITHS_DEG:
        airmass = 1.0 / math.cos(math.radians(zen))
        for wl in WAVELENGTHS_NM:
            for zkm in acc_km:
                rows["wavelength_nm"].append(int(wl))
                rows["emission_altitude_km"].append(zkm)
                rows["zenith_deg"].append(zen)
                rows["airmass"].append(airmass)
                rows["transmission"].append(sim.transmission(wl, zkm * 1000.0, 0.0, airmass))
                rows["transmission_simtools"].append(
                    float(simtools_model.transmission(float(wl), zkm * 1000.0, obs_m, airmass)))
    out = Table(rows)
    out["wavelength_nm"].unit = "nm"
    out["emission_altitude_km"].unit = "km"
    out["zenith_deg"].unit = "deg"
    out["transmission"].description = "sim_telarray atmospheric_transmission2 (telescope at obs level, no instrument OD)"
    out["transmission_simtools"].description = "simtools.atmosphere.transmission on the ECSV"
    out.meta["site"] = site
    out.meta["source_table"] = f"{instrument}/atmospheric_transmission-{version}.ecsv"
    out.meta["observatory_level_m"] = obs_m
    out.write(HERE / f"acceptance_atmosphere_{site.lower()}_{version}.ecsv",
              format="ascii.ecsv", overwrite=True)


if __name__ == "__main__":
    main(sys.argv[1])
