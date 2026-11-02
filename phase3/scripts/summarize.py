"""Print the results table (markdown) from results/<TEL>_za<ZA>.json.
usage: summarize.py [results_dir] [work_dir]
"""
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
results_dir = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "results")
work_dir = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "..", "work")

print("| telescope | zenith | route/native total PE | 1 sigma (total) | total gate (1%, 3 sigma) | matched events | per-event PE ratio | per-event PE corr | pixel corr route vs native (n events) | native-seed control | pixels >3 sigma (route / control) | event mean time diff [ns] | KS D, p (per-p.e. times) | route output sha |")
print("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
for f in sorted(glob.glob(os.path.join(results_dir, "*_za*.json"))):
    d = json.load(open(f))
    name = os.path.basename(f)[:-5]
    tel, za = name.split("_za")
    t, e, p, s = d["totals"], d["events"], d["pixels"], d["times"]
    det = json.load(open(os.path.join(work_dir, os.path.basename(d["point"]), "determinism.json")))
    det_txt = ("bunches and PE content identical" if det["bunches.iact"]["identical"]
               and det["photoelectron_content_sha256"]["identical"] else "DIFFERENT")
    gate_tot = "PASS" if t["pass_1pct"] and t["pass_3sigma"] else "FAIL"
    print(f"| {tel} | {za} | {t['ratio_detected']:.4f} | {t['sigma_rel_total']:.4f} | {gate_tot} "
          f"(dev {t['ratio_minus_1']*100:+.2f}%, 3 sigma {3*t['sigma_rel_total']*100:.2f}%) | "
          f"{e['matched_event_ids']} | {e['event_n_pe_ratio_route_over_native']:.4f} | {e['event_n_pe_pearson']:.5f} | "
          f"{e['pixel_corr_mean']:.4f} ({e['pixel_corr_n_events']}) | {e['pixel_corr_native_seed_vs_seed_mean']:.4f} | "
          f"{p['n_outside_3sigma']} / {p['control_native_seed_pair_outside_3sigma']} | "
          f"{s['event_mean_diff_ns']:+.3f} +- {s['event_mean_diff_sem_ns']:.3f} (n={s['n_events']}) | "
          f"{s['ks_D']:.4f}, {s['ks_p']:.3g} | {det_txt} |")
