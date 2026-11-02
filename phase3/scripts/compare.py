"""Compare one obdeect route run with native sim_telarray runs on the same CORSIKA IACT file.

usage (container): compare.py <point_dir> <route_tag> <native_seed> [<native_seed> ...] > out.json
  point_dir: work/<TEL>_za<ZA>; route output in route_<route_tag>/, native in native_s<seed>/.
Events are matched by sim_telarray event_id. The first native seed is the reference for the per-event
and per-pixel tests; all seeds enter the total (mean over seeds and seed spread).

Per-pixel and per-p.e. tests use only the events that carry a photo-electron (pixel) list in BOTH files.
The route output of sim_telarray has pixel lists only for the first telescope block of each shower
(see verification notes in README.md); per-event photo-electron sums (photoelectron_sums) are used for
the event-level test over all matched events.
"""
import json
import math
import re
import sys
import warnings

import numpy as np
from eventio import SimTelFile
from scipy import stats

warnings.filterwarnings("ignore")


def read_events(path):
    """Return {event_id: (pixel_ids, times, n_pe_sum)} of all telescopes in the event."""
    out = {}
    with SimTelFile(path) as f:
        for ev in f:
            pix, tim = [], []
            for _tel, d in ev.get("photoelectrons", {}).items():
                if "pixel_id" in d:
                    pix.append(np.asarray(d["pixel_id"], dtype=int))
                    tim.append(np.asarray(d["time"], dtype=float))
            pix = np.concatenate(pix) if pix else np.empty(0, dtype=int)
            tim = np.concatenate(tim) if tim else np.empty(0)
            sums = ev.get("photoelectron_sums", {})
            n_pe = float(np.sum(sums["n_pe"])) if "n_pe" in sums else float(pix.size)
            out[int(ev["event_id"])] = (pix, tim, n_pe)
    return out


def log_counts(log_path):
    text = open(log_path, errors="replace").read()
    res = {}
    for key in ("All photons", "Camera hit", "Detected", "Tel. triggered"):
        m = re.search(rf"^\s*{re.escape(key)}:?\s+(\d+)", text, re.M)
        res[key] = int(m.group(1)) if m else None
    return res


def pixel_map(pix, npix):
    return np.bincount(pix, minlength=npix)[:npix].astype(float)


def main(point, route_tag, seeds):
    ref_seed = seeds[0]
    route_dir = f"{point}/route_{route_tag}"
    rlog = log_counts(f"{route_dir}/simtel.log")
    nlogs = {s: log_counts(f"{point}/native_s{s}/simtel.log") for s in seeds}
    rev = read_events(f"{route_dir}/route.simtel.zst")
    nev = {s: read_events(f"{point}/native_s{s}/native.simtel.zst") for s in seeds}
    npix = 1 + max(int(max(v[0].max() for v in d.values() if v[0].size)) for d in [rev, *nev.values()])
    res = {"point": point, "route_tag": route_tag, "native_seeds": seeds}

    # 1. totals (all showers, sim_telarray logs)
    nd = np.array([nlogs[s]["Detected"] for s in seeds], float)
    nc = np.array([nlogs[s]["Camera hit"] for s in seeds], float)
    ratio = rlog["Detected"] / nd.mean()
    sem_native_rel = (nd.std(ddof=1) / math.sqrt(len(seeds))) / nd.mean()
    stat_route_rel = 1.0 / math.sqrt(rlog["Detected"])
    sig_tot = math.sqrt(sem_native_rel**2 + stat_route_rel**2)
    res["totals"] = {
        "route_detected": rlog["Detected"], "native_detected": nd.tolist(),
        "native_detected_mean": float(nd.mean()), "native_detected_sd_seeds": float(nd.std(ddof=1)),
        "ratio_detected": ratio, "ratio_minus_1": ratio - 1.0,
        "sigma_rel_total": sig_tot, "sigma_rel_native_seed_sem": sem_native_rel,
        "sigma_rel_route_poisson": stat_route_rel,
        "pass_1pct": bool(abs(ratio - 1.0) < 0.01), "pass_3sigma": bool(abs(ratio - 1.0) < 3 * sig_tot),
        "route_camera_hit": rlog["Camera hit"], "native_camera_hit": nc.tolist(),
        "ratio_camera_hit_vs_mean": rlog["Camera hit"] / nc.mean(),
        "route_tel_triggered": rlog["Tel. triggered"],
        "native_tel_triggered": [nlogs[s]["Tel. triggered"] for s in seeds],
        "route_all_photons_log": rlog["All photons"],
        "native_all_photons_log": [nlogs[s]["All photons"] for s in seeds],
    }

    # 2. events matched by event id
    common = sorted(set(rev) & set(nev[ref_seed]))
    ne = np.array([[rev[e][2], nev[ref_seed][e][2]] for e in common])
    res["events"] = {
        "matched_event_ids": len(common),
        "n_pe_sum_route": float(ne[:, 0].sum()), "n_pe_sum_native_seed_ref": float(ne[:, 1].sum()),
        "event_n_pe_ratio_route_over_native": float(ne[:, 0].sum() / ne[:, 1].sum()),
        "event_n_pe_pearson": float(np.corrcoef(ne[:, 0], ne[:, 1])[0, 1]),
    }
    pe_common = [e for e in common if rev[e][0].size and nev[ref_seed][e][0].size]
    res["events"]["events_with_pixel_lists_both"] = len(pe_common)
    res["events"]["event_ids_with_pixel_lists_route"] = sorted(e for e in rev if rev[e][0].size)[:60]

    corr, ctrl, dts = [], [], []
    for eid in pe_common:
        pr, tr, _ = rev[eid]
        pn, tn, _ = nev[ref_seed][eid]
        a, b = pixel_map(pr, npix), pixel_map(pn, npix)
        if a.std() > 0 and b.std() > 0:
            corr.append(np.corrcoef(a, b)[0, 1])
        dts.append(tr.mean() - tn.mean())
        if len(seeds) > 1 and nev[seeds[1]].get(eid, (np.empty(0),))[0].size:
            c = pixel_map(nev[seeds[1]][eid][0], npix)
            if a.std() > 0 and c.std() > 0:
                ctrl.append(np.corrcoef(b, c)[0, 1])
    res["events"].update({
        "pixel_corr_mean": float(np.mean(corr)), "pixel_corr_sd": float(np.std(corr, ddof=1)),
        "pixel_corr_n_events": len(corr),
        "pixel_corr_native_seed_vs_seed_mean": float(np.mean(ctrl)) if ctrl else None,
        "pass_corr_gt_0p99": bool(np.mean(corr) > 0.99)})

    # 2b. summed pixel image over the matched events with pixel lists: route vs native (seeds pooled)
    # events with pixel lists in the route and in every native seed (the seeds trigger different events)
    pe_all = [e for e in pe_common if all(e in nev[s] and nev[s][e][0].size for s in seeds)]
    sr = np.zeros(npix)
    for e in pe_all:
        sr += pixel_map(rev[e][0], npix)
    sn = {s: np.zeros(npix) for s in seeds}
    for s in seeds:
        for e in pe_all:
            sn[s] += pixel_map(nev[s][e][0], npix)
    sn_pool = sum(sn.values())
    k = len(seeds)
    sel = (sn_pool >= 1) & (sr >= 1)
    rat = np.where(sel, sr * k / np.maximum(sn_pool, 1), 1.0)
    err = np.where(sel, rat * np.sqrt(1.0 / np.maximum(sr, 1) + 1.0 / np.maximum(sn_pool, 1)), 1.0)
    z = np.where(sel, (rat - 1.0) / np.maximum(err, 1e-12), 0.0)
    # control: native seed 2 against native seed 1 (same events, no physics difference)
    zc = np.zeros(npix)
    if k > 1:
        sc, s0 = sn[seeds[1]], sn[seeds[0]]
        selc = (sc >= 1) & (s0 >= 1)
        rc = np.where(selc, sc / np.maximum(s0, 1), 1.0)
        ec = np.where(selc, rc * np.sqrt(1.0 / np.maximum(sc, 1) + 1.0 / np.maximum(s0, 1)), 1.0)
        zc = np.where(selc, (rc - 1.0) / np.maximum(ec, 1e-12), 0.0)
        n_ctrl = int((np.abs(zc) > 3).sum())
    else:
        n_ctrl = None
    res["pixels"] = {
        "events_used": len(pe_all), "npix_used": int(sel.sum()),
        "route_pe_in_sum": float(sr.sum()), "native_pe_in_sum_pooled": float(sn_pool.sum()),
        "ratio_pe_in_sum": float(sr.sum() * k / sn_pool.sum()),
        "n_outside_3sigma": int((np.abs(z) > 3).sum()),
        "expected_outside_3sigma_by_chance": round(0.0027 * int(sel.sum()), 2),
        "control_native_seed_pair_outside_3sigma": n_ctrl,
        "pass_no_pixel_outside_3sigma": bool((np.abs(z) > 3).sum() == 0)}

    # 3. times
    dts = np.asarray(dts)
    res["times"] = {"n_events": int(dts.size), "event_mean_diff_ns": float(dts.mean()),
                    "event_mean_diff_sem_ns": float(dts.std(ddof=1) / math.sqrt(dts.size)),
                    "event_mean_diff_sd_ns": float(dts.std(ddof=1)),
                    "pass_lt_0p2ns": bool(abs(dts.mean()) < 0.2)}
    for s in seeds[1:]:
        d2 = [rev[e][1].mean() - nev[s][e][1].mean() for e in pe_common if e in nev[s] and nev[s][e][1].size]
        if d2:
            res["times"][f"control_event_mean_diff_vs_native_seed_{s}_ns"] = float(np.mean(d2))
    tr_all = np.concatenate([rev[e][1] for e in pe_common]) if pe_common else np.empty(0)
    tn_all = np.concatenate([nev[ref_seed][e][1] for e in pe_common]) if pe_common else np.empty(0)
    ks = stats.ks_2samp(tr_all, tn_all)
    res["times"].update({
        "ks_pooled_pe_times": f"per-p.e. arrival times of the {len(pe_common)} matched events with pixel lists; native seed {ref_seed}",
        "ks_n_route": int(tr_all.size), "ks_n_native": int(tn_all.size),
        "ks_D": float(ks.statistic), "ks_p": float(ks.pvalue),
        "pass_ks_p_gt_1e-3": bool(ks.pvalue > 1e-3),
        "pe_time_mean_route": float(tr_all.mean()), "pe_time_mean_native": float(tn_all.mean())})
    res["pass_all"] = bool(res["totals"]["pass_1pct"] and res["totals"]["pass_3sigma"]
                           and res["events"]["pixel_corr_mean"] > 0.99
                           and res["pixels"]["pass_no_pixel_outside_3sigma"]
                           and res["times"]["pass_lt_0p2ns"] and res["times"]["ks_p"] > 1e-3)
    return res


if __name__ == "__main__":
    point, tag = sys.argv[1], sys.argv[2]
    seeds = [int(s) for s in sys.argv[3:]]
    print(json.dumps(main(point, tag, seeds), indent=1, default=float))
