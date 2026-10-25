# obdeect validation

Scripts for comparing the `obdeect` optical ray tracer with sim_telarray and
for measuring its trace and photon writer performance. The suites are split
into phase 1 optical comparisons, phase 2 calibration-light comparisons, and
performance checks. Scripts write generated data under `runs/`, `out/`, or a
caller-supplied output directory; those files are not source data.

## Environment

Use the development container image `ghcr.io/gammasim/simtools-dev`, with four
checkouts mounted as follows:

```
/workdir/external/obdeect-validation  this repository
/workdir/external/obdeect             obdeect checkout
/workdir/external/simtools            simtools checkout (branch obdeect)
/workdir/external/simulation-models   simulation-models checkout (branch simulation-model-masts)
```

The container's simulation software is available under `/workdir/simulation_software`
and its Python environment under `/workdir/env`. For example, from the parent
directory containing the four checkouts:

```sh
podman run --rm -it \
  -v "$PWD:/workdir/external" \
  -v "$PWD/../simulation_software:/workdir/simulation_software:ro" \
  ghcr.io/gammasim/simtools-dev
```

Inside the container, install or activate the checkouts' documented development
environment so `simtools-*` commands and `obdeect` are importable. Scripts accept
repository and output paths where practical; `OBDEECT_DIR`, `SIMTOOLS_DIR`,
`MODELS_DIR`, and `OUT_DIR` override container defaults.

## Phase 1: optical comparisons

`phase1/run_psf.sh <out> <model_version> <site:telescope>...` runs
`simtools-validate-optics` with both backends using the same seeds and offsets.
For a single telescope, for example:

```sh
phase1/run_psf.sh out/psf 6.0.2 North:LSTN-01
```

It compares D80, effective area, and effective focal length over field angle;
the documented acceptance is agreement within the largest deviations in
[`docs/phase1.md`](docs/phase1.md). The other scripts run incident-angle,
per-mirror, single-mirror, SCT, seed-spread, and PSF-application comparisons.
See their `--help` output or usage comments for arguments.

## Phase 2: calibration light

`phase2/cases.sh [all|flashers|north|south|off_axis]` runs the configured
flasher and illuminator cases with both ray-tracing backends and two seed sets.
Runs and logs are written beneath `phase2/runs/`. The comparisons and
acceptance criteria are in [`docs/phase2.md`](docs/phase2.md).

## Performance

`perf/make_models.py [telescope ...]` regenerates local optical models from
the simulation-models checkout. Compiled models are derived CTAO data and are
ignored by git. `perf/replay_all.sh <obdeect checkout> <output dir>` builds a
platform-local reference replay from obdeect `main`, builds the current replay,
and compares output. Do not transfer replay `.bin` references between hosts:
floating point math can differ by platform/libm. `perf/bench_hw.sh <obdeect checkout>
<new output dir>` runs compiler and trace benchmarks and replay checks.
Additional Python and writer benchmarks are in `perf/`.

## Provenance and results

For each result set, record the full commit hashes of this repository,
`obdeect`, `simtools`, and `simulation-models`, plus the container image digest
(for example, `podman image inspect --format '{{.Digest}}'`). Keep this manifest
beside the output directory. Results belong in `runs/` or `out/`; do not add
results, photon lists, logs, plots, or replay files to version control.
