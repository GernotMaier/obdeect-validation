"""Markdown summary of the validation cases (reads runs/*/summary.json from compare.py).

Usage: python summarize.py [case ...]
"""

import json
import sys
from pathlib import Path

import numpy as np

RUNS = Path(__file__).parent / "runs"
cases = sys.argv[1:] or sorted(p.name for p in RUNS.iterdir() if (p / "summary.json").exists())


def combined(runs, backend, name):
    """Mean over the seed sets of one backend and its standard error."""
    values = [r for n, r in runs.items() if n.startswith(backend)]
    mean = np.mean([r[name] for r in values])
    error = np.sqrt(np.sum([r[f"{name}_err"] ** 2 for r in values])) / len(values)
    return mean, error


print(
    "| Case | p.e./event sim_telarray | p.e./event obdeect | ratio | centre shift [mm] |"
    " width ratio | time rms [ns] | pixel shape pull rms (cross / same backend) | wall [s] |"
)
print("| --- | --- | --- | --- | --- | --- | --- | --- | --- |")
for case in cases:
    result = json.loads((RUNS / case / "summary.json").read_text())
    runs = result["runs"]
    pe_s, err_s = combined(runs, "sim_telarray", "pe")
    pe_o, err_o = combined(runs, "obdeect", "pe")
    ratio = pe_o / pe_s
    ratio_err = ratio * np.hypot(err_s / pe_s, err_o / pe_o)
    shift = np.hypot(
        combined(runs, "obdeect", "cx")[0] - combined(runs, "sim_telarray", "cx")[0],
        combined(runs, "obdeect", "cy")[0] - combined(runs, "sim_telarray", "cy")[0],
    )
    width = combined(runs, "obdeect", "width")[0] / combined(runs, "sim_telarray", "width")[0]
    time_s, time_o = (combined(runs, b, "time_rms")[0] for b in ("sim_telarray", "obdeect"))
    pairs = result["pairs"]
    cross = np.mean(
        [p["shape_pull_rms"] for n, p in pairs.items() if "obdeect" in n and "sim" in n]
    )
    same = np.mean(
        [p["shape_pull_rms"] for n, p in pairs.items() if not ("obdeect" in n and "sim" in n)]
    )
    wall = {b: np.mean([r["wall_s"] for n, r in runs.items() if n.startswith(b)])
            for b in ("sim_telarray", "obdeect")}
    print(
        f"| {case} | {pe_s:.0f} ± {err_s:.0f} | {pe_o:.0f} ± {err_o:.0f} |"
        f" {ratio:.4f} ± {ratio_err:.4f} | {1000 * shift:.1f} | {width:.4f} |"
        f" {time_s:.2f} / {time_o:.2f} | {cross:.2f} / {same:.2f} |"
        f" {wall['sim_telarray']:.0f} / {wall['obdeect']:.0f} |"
    )
