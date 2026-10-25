#!/bin/bash
# One validation case with both backends and two seed sets (run-to-run scatter).
# Usage: run_case.sh <case> flasher|illuminator <application arguments>
case=$1; app=$2; shift 2
HERE=$(cd "$(dirname "$0")" && pwd)
OUT_DIR=${OUT_DIR:-$HERE/runs}
case "$OUT_DIR" in /*) ;; *) OUT_DIR=$PWD/$OUT_DIR ;; esac
SIMTOOLS_DIR=${SIMTOOLS_DIR:-/workdir/external/simtools}
out=$OUT_DIR/$case
cd "$SIMTOOLS_DIR"
for backend in ${BACKENDS:-sim_telarray obdeect}; do
  for seed in ${SEEDS:-11 12}; do
    dir=$out/$backend-$seed
    mkdir -p "$dir"
    if [ $app = flasher ]; then
      command=(simtools-simulate-flasher --run_mode full_simulation --run_number 10)
    else
      command=(simtools-simulate-illuminator)
    fi
    python "$HERE/timed.py" "$dir.time.json" "${command[@]}" "$@" \
      --model_version 7.0.0 --output_path $dir --ray_tracing_backend $backend \
      --instrument_seed $seed --simulation_seed $((seed + 100)) > "$dir.log" 2>&1 \
      || echo "FAILED $case $backend $seed"
    echo "$case $backend $seed: $(python -c "import json; r=json.load(open('$dir.time.json')); print(f\"{r['wall_s']:.0f} s, {r['max_rss_mb']:.0f} MB\")")"
  done
done
