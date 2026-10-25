"""Benchmark of the simtools photon bunch writer, old versus new code.

Writes 4e7 random photon bunches in 100 events, uncompressed (``.iact``) and
gzip compressed (``.iact.gz``), with the old and the new ``write_photon_bunches``;
best of three per variant, alternating old and new. Reports MB/s (1 MB = 1e6
bytes, of the output file, compression included) and whether the content
(decompressed for ``.gz``) is byte-identical. There is no speed gate.

The old module is the version before the zero-copy writer, taken from git:

    git -C <simtools repo> show e98013d:src/simtools/simtel/photon_bunch_file.py > <dir>/old_photon_bunch_file.py

Usage (simtools venv; the output files go to the work directory and are removed):

    <simtools>/.venv/bin/python bench_writer.py <dir>/old_photon_bunch_file.py <work dir>

Each event reuses one array of random bunches, so memory stays at about 15 MB.
"""

import argparse
import gzip
import hashlib
import importlib.util
import os
import time
from pathlib import Path

import astropy.units as u
import numpy as np
from astropy.table import Table

import simtools.simtel.photon_bunch_file as new_module

CHUNK_BYTES = 1 << 24


def load_old_module(path):
    spec = importlib.util.spec_from_file_location("old_photon_bunch_file", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def atmospheric_profile():
    return Table(
        {
            "altitude": [0.0, 2.0, 10.0] * u.km,
            "density": [1.2e-3, 1.0e-3, 4.0e-4] * u.g / u.cm**3,
            "thickness": [1030.0, 800.0, 270.0] * u.g / u.cm**2,
            "refractive_index": [2.8e-4, 2.3e-4, 1.0e-4],
        }
    )


def random_bunches(rng, n):
    bunches = np.zeros(n, dtype=new_module.BUNCH_DTYPE)
    for name in new_module.BUNCH_DTYPE.names:
        bunches[name] = rng.uniform(-50.0, 50.0, n)
    bunches["photons"] = rng.uniform(0.0, 1.0, n)
    return bunches


def write(module, path, events):
    start = time.perf_counter()
    module.write_photon_bunches(
        path,
        events,
        observation_level_m=2147.0,
        telescope_radius_m=2.0,
        atmospheric_profile=atmospheric_profile(),
        run_number=7,
    )
    return time.perf_counter() - start


def content_sha256(path):
    digest = hashlib.sha256()
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rb") as stream:
        for chunk in iter(lambda: stream.read(CHUNK_BYTES), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("old_module", type=Path, help="old photon_bunch_file.py (see docstring)")
    parser.add_argument("work_dir", type=Path, help="directory for the output files")
    parser.add_argument("--bunches", type=int, default=40_000_000, help="total bunches")
    parser.add_argument("--events", type=int, default=100, help="number of events")
    parser.add_argument("--repeats", type=int, default=3, help="repeats per variant (best kept)")
    args = parser.parse_args()

    args.work_dir.mkdir(parents=True, exist_ok=True)
    event = random_bunches(np.random.default_rng(20261025), args.bunches // args.events)
    events = [event] * args.events
    modules = {"old": load_old_module(args.old_module), "new": new_module}

    print(f"bunches={len(event) * args.events} events={args.events} repeats={args.repeats}")
    for suffix in ("iact", "iact.gz"):
        best, size_mb, sha = {}, {}, {}
        for _ in range(args.repeats):
            for name, module in modules.items():
                path = args.work_dir / f"{name}.{suffix}"
                seconds = write(module, path, events)
                size_mb[name] = os.path.getsize(path) / 1e6
                best[name] = min(best.get(name, np.inf), seconds)
                if name not in sha:
                    sha[name] = content_sha256(path)
                os.remove(path)
                print(f"{suffix:8s} {name:3s} {seconds:8.3f} s {size_mb[name] / seconds:9.1f} MB/s")
        for name in modules:
            print(
                f"RESULT {suffix:8s} {name:3s} best={best[name]:.3f} s "
                f"size={size_mb[name]:.1f} MB mb_per_s={size_mb[name] / best[name]:.1f} "
                f"identical_to_old={sha[name] == sha['old']}"
            )


if __name__ == "__main__":
    main()
