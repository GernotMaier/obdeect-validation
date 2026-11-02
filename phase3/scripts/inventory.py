"""Statistics of one point: IACT blocks, bunch rows and photons in; route bunch rows and photons out;
sim_telarray events and photo-electrons written. usage (container): inventory.py <point_dir> <tel> <za> <route_tag> <native_seed>
"""
import json
import sys
import warnings

import numpy as np
from eventio import SimTelFile
from simtools.corsika.photon_bunches import read_photon_bunches

warnings.filterwarnings("ignore")
point, tel, za, rtag, nseed = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5]


def bunch_stats(path):
    blocks = rows = 0
    photons = 0.0
    for ev in read_photon_bunches(path):
        blocks += 1
        rows += len(ev["x"])
        photons += float(np.sum(ev["size"]))
    return {"blocks": blocks, "bunch_rows": rows, "photons": photons}


def simtel_stats(path):
    n_ev = n_pe = n_pe_lists = 0
    with SimTelFile(path) as f:
        for ev in f:
            n_ev += 1
            for _t, d in ev.get("photoelectrons", {}).items():
                n_pe_lists += 1
                n_pe += len(np.asarray(d.get("pixel_id", [])))
    return {"events": n_ev, "events_with_pixel_lists": n_pe_lists, "pe_in_pixel_lists": n_pe}


out = {
    "iact_in": bunch_stats(f"{point}/gamma_{tel}_za{za}.iact"),
    "route_out": bunch_stats(f"{point}/route_{rtag}/bunches.iact"),
    "route_simtel": simtel_stats(f"{point}/route_{rtag}/route.simtel.zst"),
    "native_simtel": simtel_stats(f"{point}/native_s{nseed}/native.simtel.zst"),
}
print(json.dumps(out))
