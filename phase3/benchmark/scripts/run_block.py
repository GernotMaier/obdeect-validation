"""Benchmark blocks of P10, run inside the container obdeect-val (eventio/simtools python).

usage: run_block.py <block>
blocks: lsts01_native, lsts01_route, lsts01_profile, lsts01_bypass, lsts01_conc1, lsts01_conc3,
        lsts01_conc6, msts04_native, msts04_route, msts04_bypass, kernel, writer

Each timed run goes through timed.py (wall, user/sys CPU, peak RSS of the child) and is appended
as one JSON line to results/<block>.jsonl. Outputs go to work/<block>/... (not kept in the project
except the small logs). The host driver (run_p10.sh) records the load before and after each block.
"""

import glob
import json
import os
import shutil
import subprocess
import sys
import time

B = "/workdir/external/obdeect-validation/phase3/benchmark"
PY = "/workdir/env/bin/python"
TIMED = f"{B}/scripts/timed.py"
SIMTEL = "/workdir/simulation_software/sim_telarray/bin/sim_telarray"
MODELS = "/workdir/external/simulation-models"
REPEATS = 3
THREADS_SCALING = [1, 2, 4, 6]
N_CONCURRENT = [1, 3, 6]
KERNEL_PHOTONS = 2_000_000

INPUTS = {
    "lsts01": {
        "iact": glob.glob(f"{B}/input/lsts01/corsika/run000001/*.corsika.zst")[0],
        "card": glob.glob(f"{B}/input/lsts01/corsika/run000001/*.corsika.input")[0],
        "tmap": f"{B}/input/lsts01_telescope_map.json",
        "model": "/workdir/external/val/phase3/prod/final_disk/model/run000001/7.0.0",
        "cfg": "CTAO-South-LSTS-01.cfg",
    },
    "msts04": {
        "iact": glob.glob(f"{B}/input/msts04/corsika/run000001/*.corsika.zst")[0],
        "card": glob.glob(f"{B}/input/msts04/corsika/run000001/*.corsika.input")[0],
        "tmap": f"{B}/input/msts04_telescope_map.json",
        "model": "/workdir/external/val/phase3/mstref/model/run000001/7.0.0",
        "cfg": "CTAO-South-MSTS-04.cfg",
    },
}


def run_timed(label, prefix, cmd):
    """Run cmd through timed.py and return its JSON record."""
    out = subprocess.run(
        [PY, TIMED, label, prefix, *cmd], capture_output=True, text=True, check=True
    )
    return json.loads(out.stdout.strip().splitlines()[-1])


def record(block, rec):
    with open(f"{B}/results/{block}.jsonl", "a") as stream:
        stream.write(json.dumps(rec) + "\n")
    print(json.dumps(rec), flush=True)


def route_cmd(inp, threads, out, tmpdir):
    cfg = INPUTS[inp]
    return [
        PY, "-m", "simtools.simtel.shower_route",
        "--telescope-map", cfg["tmap"], "--telescope-ids", "0",
        "--input", cfg["iact"], "--output", out,
        "--corsika-card", cfg["card"],
        "--simulation-models-path", MODELS,
        "--threads", str(threads), "--output-path", tmpdir,
    ]  # fmt: skip


def simtel_cmd(inp, bypass, outdir, input_file, tag):
    cfg = INPUTS[inp]
    m = cfg["model"]
    return [
        SIMTEL, "-c", f"{m}/{cfg['cfg']}", f"-I{m}",
        f"-C", f"histogram_file={outdir}/{tag}.hdata.zst",
        "-C", "random_state=none",
        "-C", f"output_file={outdir}/{tag}.simtel.zst",
        "-C", "random_seed=4242",
        "-C", "telescope_theta=20.0", "-C", "telescope_phi=0.0",
        "-C", "power_law=2.5",
        "-C", f"Bypass_Optics={bypass}",
        "-C", f"input_file={input_file}",
    ]  # fmt: skip


def size_mb(path):
    return round(os.path.getsize(path) / 1e6, 2) if os.path.exists(path) else None


def block_native(inp):
    outdir = f"{B}/work/{inp}_native"
    os.makedirs(outdir, exist_ok=True)
    for rep in range(1, REPEATS + 1):
        rec = run_timed(f"native_{inp}_r{rep}", f"{outdir}/r{rep}",
                        simtel_cmd(inp, 0, outdir, INPUTS[inp]["iact"], f"r{rep}"))
        rec.update(case="native_bypass0", input=inp, rep=rep,
                   output_mb=size_mb(f"{outdir}/r{rep}.simtel.zst"))
        record(f"{inp}_native", rec)
        os.remove(f"{outdir}/r{rep}.simtel.zst")  # keep disk use low; the size is recorded


def block_route(inp, thread_list, case_prefix):
    for threads in thread_list:
        outdir = f"{B}/work/{inp}_route/t{threads}"
        for rep in range(1, REPEATS + 1):
            rdir = f"{outdir}/r{rep}"
            os.makedirs(f"{rdir}/tmp", exist_ok=True)
            out = f"{rdir}/camera.iact.gz"
            rec = run_timed(f"route_{inp}_t{threads}_r{rep}", f"{rdir}/route",
                            route_cmd(inp, threads, out, f"{rdir}/tmp"))
            rec.update(case=f"{case_prefix}route", input=inp, threads=threads, rep=rep,
                       output_mb=size_mb(out))
            record(f"{inp}_route", rec)
            if rep > 1 or threads > 1:
                shutil.rmtree(rdir)  # keep only the first rep of 1 thread for the bypass step


def block_profile(inp):
    rdir = f"{B}/work/{inp}_profile"
    os.makedirs(f"{rdir}/tmp", exist_ok=True)
    prof = f"{rdir}/route.prof"
    cmd = [PY, "-m", "cProfile", "-o", prof, "-m", "simtools.simtel.shower_route"]
    cmd += route_cmd(inp, 1, f"{rdir}/camera.iact.gz", f"{rdir}/tmp")[3:]
    rec = run_timed(f"profile_{inp}", f"{rdir}/route", cmd)
    rec.update(case="route_cprofile", input=inp, threads=1, rep=1,
               output_mb=size_mb(f"{rdir}/camera.iact.gz"))
    record(f"{inp}_profile", rec)


def block_bypass(inp):
    src = f"{B}/work/{inp}_route/t1/r1/camera.iact.gz"
    outdir = f"{B}/work/{inp}_bypass"
    os.makedirs(outdir, exist_ok=True)
    for rep in range(1, REPEATS + 1):
        rec = run_timed(f"bypass_{inp}_r{rep}", f"{outdir}/r{rep}",
                        simtel_cmd(inp, 1, outdir, src, f"r{rep}"))
        rec.update(case="sim_telarray_bypass1_on_route_output", input=inp, rep=rep,
                   output_mb=size_mb(f"{outdir}/r{rep}.simtel.zst"))
        record(f"{inp}_bypass", rec)
        os.remove(f"{outdir}/r{rep}.simtel.zst")


def mem_available_mb():
    with open("/proc/meminfo") as stream:
        for line in stream:
            if line.startswith("MemAvailable:"):
                return int(line.split()[1]) / 1024
    return 0.0


def block_conc(n):
    """N concurrent single-thread routes on N copies of the LSTS-01 input; one set = one repeat.

    Guard: a set is skipped (and recorded as skipped) when MemAvailable is below 250 MB per process,
    so that the benchmark cannot push the shared container into an out-of-memory kill.
    """
    inp = "lsts01"
    cdir = f"{B}/work/conc_copies"
    os.makedirs(cdir, exist_ok=True)
    src = INPUTS[inp]["iact"]
    for rep in range(1, REPEATS + 1):
        avail = mem_available_mb()
        if avail < 250 * n:
            record(f"{inp}_conc{n}", {"case": "concurrent_route", "concurrent": n, "rep": rep,
                                      "skipped": f"MemAvailable {avail:.0f} MB < {250 * n} MB"})
            continue
        procs = []
        t0 = time.perf_counter()
        rdir = f"{B}/work/conc{n}/r{rep}"
        os.makedirs(rdir, exist_ok=True)
        for i in range(n):
            copy = f"{cdir}/copy{i}.corsika.zst"
            if not os.path.exists(copy):
                shutil.copyfile(src, copy)
            tmp = f"{rdir}/p{i}/tmp"
            os.makedirs(tmp, exist_ok=True)
            cmd = route_cmd(inp, 1, f"{rdir}/p{i}/camera.iact.gz", tmp)
            cmd[cmd.index("--input") + 1] = copy
            procs.append(subprocess.Popen(
                [PY, TIMED, f"conc{n}_p{i}_r{rep}", f"{rdir}/p{i}/route", *cmd],
                stdout=subprocess.PIPE, text=True))  # fmt: skip
        results = [json.loads(p.communicate()[0].strip().splitlines()[-1]) for p in procs]
        wall_set = time.perf_counter() - t0
        for r in results:
            r.update(case="concurrent_route", input=inp, concurrent=n, rep=rep,
                     set_wall_s=round(wall_set, 3))
            record(f"{inp}_conc{n}", r)
        shutil.rmtree(f"{rdir}/p0", ignore_errors=True)
        for i in range(n):
            shutil.rmtree(f"{rdir}/p{i}", ignore_errors=True)


def block_kernel():
    script = "/workdir/external/val/perf/bench_bunches.py"
    model = "/workdir/external/val/perf/models/MSTS-04.json"
    for threads in (1, 6):
        for rep in range(1, REPEATS + 1):
            out = subprocess.run([PY, script, model, str(KERNEL_PHOTONS), str(threads)],
                                 capture_output=True, text=True, check=True).stdout
            rec = {"case": "kernel_bench_bunches", "threads": threads, "rep": rep,
                   "photons": KERNEL_PHOTONS, "lines": out.strip().splitlines()}
            record("kernel", rec)


def block_writer():
    """bench_writer.py with 3 repeats; the per-write times are parsed by summarize.py."""
    out = subprocess.run(
        [PY, "/workdir/external/val/perf/bench_writer.py", f"{B}/scripts/old_photon_bunch_file.py",
         f"{B}/work/writer", "--repeats", str(REPEATS)],
        capture_output=True, text=True, check=True,
    ).stdout
    record("writer", {"case": "bench_writer", "repeats": REPEATS, "lines": out.strip().splitlines()})


def main():
    block = sys.argv[1]
    os.makedirs(f"{B}/results", exist_ok=True)
    if block.endswith("_native"):
        block_native(block.split("_")[0])
    elif block.endswith("_bypass"):
        block_bypass(block.split("_")[0])
    elif block == "lsts01_route":
        block_route("lsts01", THREADS_SCALING, "")
    elif block == "msts04_route":
        block_route("msts04", [1], "")
    elif block == "lsts01_profile":
        block_profile("lsts01")
    elif block.startswith("lsts01_conc"):
        block_conc(int(block.removeprefix("lsts01_conc")))
    elif block == "kernel":
        block_kernel()
    elif block == "writer":
        block_writer()
    else:
        raise SystemExit(f"unknown block {block}")


if __name__ == "__main__":
    main()
