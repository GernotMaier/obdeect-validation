"""Per-event image shape (p.e.-weighted centroid and rms width) for route r19 vs native seeds.
usage: hillas.py <point_dir> <route_tag> <seed_ref> <seed_ctrl>   (prints JSON)
Pass if mean difference is consistent with the control: |mean_route| <= sd_control (per component).
"""
import json, sys, warnings
import numpy as np
from eventio import SimTelFile
warnings.filterwarnings("ignore")

point, tag, s_ref, s_ctl = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])

def read(path, npix):
    out, cam, n_tot, n_pix_ev, n_multi = {}, None, 0, 0, 0
    with SimTelFile(path) as f:
        if cam is None:
            td = f.telescope_descriptions
            tid = list(td.keys())[0]
            cs = td[tid]["camera_settings"]
            cam = (np.asarray(cs["pixel_x"], float), np.asarray(cs["pixel_y"], float))
        for ev in f:
            n_tot += 1
            tels = ev.get("photoelectrons", {})
            if len(tels) > 1:
                n_multi += 1
            for _t, d in tels.items():
                if "pixel_id" in d and np.size(d["pixel_id"]):
                    n_pix_ev += 1
                    cnt = np.bincount(np.asarray(d["pixel_id"], int), minlength=npix)[:npix].astype(float)
                    out[int(ev["event_id"])] = cnt
                    break
    return out, cam, dict(n_events=n_tot, n_with_pixel_lists=n_pix_ev, n_multi_tel=n_multi)

def shape(cnt, x, y):
    w = cnt.sum()
    cx = (cnt * x).sum() / w
    cy = (cnt * y).sum() / w
    rms = np.sqrt((cnt * ((x - cx) ** 2 + (y - cy) ** 2)).sum() / w)
    return np.array([cx, cy, rms])

def stats_of(d):
    d = np.asarray(d)
    return {"mean": float(d.mean()), "sem": float(d.std(ddof=1) / np.sqrt(len(d))), "sd": float(d.std(ddof=1))}

with SimTelFile(f"{point}/route_{tag}/route.simtel.zst") as f0:
    _cs = f0.telescope_descriptions[list(f0.telescope_descriptions.keys())[0]]["camera_settings"]
npix = len(_cs["pixel_x"])
route, cam, rinfo = read(f"{point}/route_{tag}/route.simtel.zst", npix)
nat_ref, _, ninfo_ref = read(f"{point}/native_s{s_ref}/native.simtel.zst", npix)
nat_ctl, _, ninfo_ctl = read(f"{point}/native_s{s_ctl}/native.simtel.zst", npix)
x, y = cam
common = sorted(set(route) & set(nat_ref) & set(nat_ctl))
R = np.array([shape(route[e], x, y) for e in common])
N = np.array([shape(nat_ref[e], x, y) for e in common])
C = np.array([shape(nat_ctl[e], x, y) for e in common])
dR = R - N   # route - native (seed ref)
dC = C - N   # control: seed ctl - seed ref
res = {"point": point, "n_common_events": len(common),
       "route_info": rinfo, "native_ref_info": ninfo_ref, "native_ctl_info": ninfo_ctl,
       "camera_pixel_x_range": [float(x.min()), float(x.max())],
       "units": "camera coordinates as stored in sim_telarray camera_settings"}
names = ["cx", "cy", "rms"]
gate = True
for i, nm in enumerate(names):
    r = stats_of(dR[:, i]); c = stats_of(dC[:, i])
    ok = abs(r["mean"]) <= c["sd"]
    gate = gate and ok
    res[nm] = {"route_minus_native": r, "control_seed_minus_seed": c, "pass_within_control_sd": bool(ok)}
# centroid shift magnitude (same event)
mR = stats_of(np.hypot(dR[:, 0], dR[:, 1])); mC = stats_of(np.hypot(dC[:, 0], dC[:, 1]))
res["centroid_shift_mag"] = {"route_minus_native": mR, "control_seed_minus_seed": mC}
res["pass_shape_gate"] = bool(gate)
print(json.dumps(res, indent=1, default=float))
