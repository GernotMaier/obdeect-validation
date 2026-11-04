"""R21 check: pixel lists per telescope event, route output vs native sim_telarray.

usage (container): pixel_list_check.py <point_dir> <route_tag> <native_seed>
Counts, for route and native files: input events, telescope events (telescope entries in the event
photo-electron tables), telescope events with a pixel list (pixel_id), and events with at least one pixel list.
"""
import json
import sys
import warnings

from eventio import SimTelFile

warnings.filterwarnings("ignore")


def count(path):
    res = {"events": 0, "telescope_events_pe_block": 0, "telescope_events_with_pixel_list": 0,
           "events_with_pixel_list": 0, "telescope_events_without_pixel_list": 0}
    with SimTelFile(path) as f:
        for ev in f:
            res["events"] += 1
            pe = ev.get("photoelectrons", {})
            n_with = 0
            for _tel, d in pe.items():
                res["telescope_events_pe_block"] += 1
                if "pixel_id" in d:
                    res["telescope_events_with_pixel_list"] += 1
                    n_with += 1
                else:
                    res["telescope_events_without_pixel_list"] += 1
            if n_with:
                res["events_with_pixel_list"] += 1
    return res


point, tag, seed = sys.argv[1], sys.argv[2], sys.argv[3]
out = {"point": point, "route": count(f"{point}/route_{tag}/route.simtel.zst"),
       "native": count(f"{point}/native_s{seed}/native.simtel.zst")}
out["route_pixel_list_fraction"] = (out["route"]["telescope_events_with_pixel_list"]
                                    / max(out["route"]["telescope_events_pe_block"], 1))
out["pass_every_telescope_event_has_pixel_list"] = bool(
    out["route"]["telescope_events_pe_block"] > 0
    and out["route"]["telescope_events_without_pixel_list"] == 0)
print(json.dumps(out, indent=1))
