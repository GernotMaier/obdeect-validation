"""Compare the sim_telarray outputs of one validation case: both backends, two seed sets.

Usage: python compare.py <case directory> [<case directory> ...]

Per run: triggered events, photoelectrons per event, image centroid and width,
time spread of the photoelectrons, readout charge and peak sample of the camera
sum. Per pair of runs: the ratio of photoelectrons per event and the per-pixel
pull of the summed images, (b - a) / sqrt(a + b), whose spread is 1 for Poisson
fluctuations only. The pairs sim_telarray/sim_telarray and obdeect/obdeect (other
seeds) give the run-to-run scatter each comparison is judged against.
"""

import json
import sys
from pathlib import Path

import numpy as np
from eventio import SimTelFile


def read_run(path):
    """Per-event quantities and the summed image of one sim_telarray output."""
    events = []
    image, x, y = None, None, None
    with SimTelFile(str(path)) as f:
        camera = next(iter(f.telescope_descriptions.values()))["camera_settings"]
        x, y = np.asarray(camera["pixel_x"]), np.asarray(camera["pixel_y"])
        for event in f:
            photo = next(iter(event.get("photoelectrons", {}).values()), None)
            if photo is None:
                continue
            counts = photo["photoelectrons"].astype(float)
            total = counts.sum()
            if total <= 0:
                continue
            image = counts if image is None else image + counts
            cx, cy = np.average(x, weights=counts), np.average(y, weights=counts)
            width = np.sqrt(np.average((x - cx) ** 2 + (y - cy) ** 2, weights=counts) / 2.0)
            times = np.asarray(photo["time"], dtype=float)
            record = {
                "pe": total,
                "cx": cx,
                "cy": cy,
                "width": width,
                "time_rms": float(np.std(times)) if len(times) > 1 else 0.0,
            }
            telescope = next(iter(event.get("telescope_events", {}).values()), None)
            if telescope is not None and "adc_samples" in telescope:
                waveform = telescope["adc_samples"][0].sum(axis=0).astype(float)
                waveform -= np.median(waveform[:3])
                record["charge"] = waveform.sum()
                record["peak"] = (waveform * np.arange(len(waveform))).sum() / waveform.sum()
            events.append(record)
    return events, image


def summary(events):
    """Mean and standard error of each per-event quantity."""
    result = {"events": len(events)}
    for name in events[0]:
        values = np.array([e[name] for e in events if name in e])
        result[name] = float(values.mean())
        result[f"{name}_err"] = float(values.std(ddof=1) / np.sqrt(len(values)))
        result[f"{name}_rms"] = float(values.std(ddof=1))
    return result


def pair(a, b):
    """Ratio b/a of photoelectrons per event and the per-pixel pull spread."""
    (sa, ia), (sb, ib) = a, b
    ratio = sb["pe"] / sa["pe"]
    error = ratio * np.hypot(sa["pe_err"] / sa["pe"], sb["pe_err"] / sb["pe"])
    # Images scaled to the same number of events.
    na, nb = sa["events"], sb["events"]
    lit = (ia > 0) | (ib > 0)
    pull = (ib[lit] / nb - ia[lit] / na) / np.sqrt(ia[lit] / na**2 + ib[lit] / nb**2)
    # Shape only: b scaled to the total of a.
    scale = ia.sum() / ib.sum()
    shape = (scale * ib[lit] - ia[lit]) / np.sqrt(ia[lit] + scale**2 * ib[lit])
    return {
        "ratio": ratio,
        "ratio_err": error,
        "pull_rms": float(pull.std()),
        "shape_pull_rms": float(shape.std()),
        "lit": int(lit.sum()),
    }


def compare(case):
    runs = {}
    for directory in sorted(Path(case).glob("*-*")):
        if not directory.is_dir():
            continue
        files = list(directory.glob("sim_telarray/*.simtel.zst"))
        if not files:
            print(f"{directory}: no output")
            continue
        events, image = read_run(files[0])
        if not events:
            print(f"{directory}: no events with photoelectrons")
            continue
        timing = json.loads(Path(f"{directory}.time.json").read_text())
        runs[directory.name] = (summary(events) | {"wall_s": timing["wall_s"]}, image)
    names = sorted(runs)
    result = {"case": Path(case).name, "runs": {n: runs[n][0] for n in names}, "pairs": {}}
    by_backend = {}
    for name in names:
        by_backend.setdefault(name.split("-")[0], []).append(name)
    reference = by_backend.get("sim_telarray", [])
    for backend, members in by_backend.items():
        if len(members) == 2:
            result["pairs"][f"{members[1]} / {members[0]}"] = pair(*(runs[m] for m in members))
    for first, second in zip(reference, by_backend.get("obdeect", [])):
        result["pairs"][f"{second} / {first}"] = pair(runs[first], runs[second])
    return result


def show(result):
    print(f"== {result['case']}")
    for name, s in result["runs"].items():
        line = (
            f"  {name:16s} events {s['events']:4d}  pe/event {s['pe']:9.1f} +- {s['pe_err']:6.1f}"
            f"  centre ({s['cx'] * 100:7.3f}, {s['cy'] * 100:7.3f}) cm  width {s['width'] * 100:6.3f}"
            f" cm  t_rms {s['time_rms']:6.3f} ns"
        )
        if "charge" in s:
            line += f"  charge {s['charge']:9.1f}  peak {s['peak']:6.2f}"
        print(line + f"  {s['wall_s']:6.0f} s")
    for name, p in result["pairs"].items():
        print(
            f"  {name:34s} ratio {p['ratio']:.4f} +- {p['ratio_err']:.4f}"
            f"  pixel pull rms {p['pull_rms']:.2f}, shape only {p['shape_pull_rms']:.2f}"
            f" ({p['lit']} pixels)"
        )


if __name__ == "__main__":
    results = []
    for case in sys.argv[1:]:
        result = compare(case)
        show(result)
        results.append(result)
        (Path(case) / "summary.json").write_text(json.dumps(result, indent=1), encoding="utf-8")
