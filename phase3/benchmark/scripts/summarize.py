"""Min and median over the repeats of each P10 case, from results/*.jsonl and results/kernel|writer.

usage: summarize.py <benchmark dir>   (prints markdown tables to stdout)
Photon and event counts come from results/input_counts.jsonl.
"""

import glob
import json
import os
import statistics
import sys

base = sys.argv[1]
res = os.path.join(base, "results")


def rows(block):
    path = os.path.join(res, f"{block}.jsonl")
    if not os.path.exists(path):
        return []
    with open(path) as stream:
        return [json.loads(line) for line in stream if line.strip()]


def stat(values):
    values = [v for v in values if v is not None]
    if not values:
        return "n/a"
    return f"{min(values):.2f} / {statistics.median(values):.2f}"


counts = {}
for line in open(os.path.join(res, "input_counts.jsonl")):
    if line.strip():
        c = json.loads(line)
        key = "lsts01" if "LSTS-01" in c["file"] else "msts04"
        counts[key] = c

print("## Input (50 showers, 1 TeV gamma, za 20 deg)")
for key, c in counts.items():
    print(f"- {key}: events {c['events']}, IACT data blocks {c['iact_data_blocks']}, "
          f"bunches {c['bunches']}, photons {c['photons']}")
print()

print("## Per-case min / median (wall s, CPU s, peak RSS MB, n)")
print("| case | input | wall min/med | cpu min/med | maxrss MB | output MB | n |")
print("|---|---|---|---|---|---|---|")
groups = {}
for block in ["lsts01_native", "lsts01_route", "lsts01_bypass", "msts04_native",
              "msts04_route", "msts04_bypass"]:
    for r in rows(block):
        key = (r["case"], r["input"], r.get("threads"))
        groups.setdefault(key, []).append(r)
for (case, inp, threads), rs in groups.items():
    name = case if threads is None else f"{case} t={threads}"
    print(
        f"| {name} | {inp} | {stat([r['wall_s'] for r in rs])} | "
        f"{stat([r['cpu_s'] for r in rs])} | "
        f"{max(r['maxrss_mb'] for r in rs):.0f} | "
        f"{rs[0].get('output_mb')} | {len(rs)} |"
    )
print()

print("## Concurrent route processes (LSTS-01, 1 thread each)")
print("| N | set wall min/med (s) | per-process wall min/med | throughput (showers/s, min-med) | n |")
print("|---|---|---|---|---|")
for n in (1, 3, 6):
    rs = rows(f"lsts01_conc{n}")
    done = [r for r in rs if "skipped" not in r]
    skipped = [r for r in rs if "skipped" in r]
    if not done:
        note = skipped[0]["skipped"] if skipped else "not run"
        print(f"| {n} | not measured: {note} | | | 0 |")
        continue
    sets = {}
    for r in done:
        sets.setdefault(r["rep"], []).append(r)
    set_walls = [rs_[0]["set_wall_s"] for rs_ in sets.values()]
    proc_walls = [r["wall_s"] for r in done]
    thr = [n * 50 / w for w in set_walls]
    print(f"| {n} | {stat(set_walls)} | {stat(proc_walls)} | "
          f"{min(thr):.2f} / {statistics.median(thr):.2f} | {len(sets)} |")
print()

print("## Kernel (bench_bunches.py, MSTS-04 model, 2e6 star photons, best of 3 per script run)")
kernel = rows("kernel")
for threads in (1, 6):
    rs = [r for r in kernel if r["threads"] == threads]
    for r in rs:
        print(f"- threads {threads} rep {r['rep']}: " + " | ".join(r["lines"]))
print()

print("## Writer (bench_writer.py, 3 repeats; per-write seconds)")
for r in rows("writer"):
    for line in r["lines"]:
        print(f"- {line}")
