#!/bin/bash
# Phase 1 open items: the PSF applications with both backends.
# Usage: apps.sh <app> <out> [extra args]
app=$1; out=$2; shift 2
SIMTOOLS_DIR=${SIMTOOLS_DIR:-/workdir/external/simtools}
case "$out" in /*) ;; *) out=$PWD/$out ;; esac
cd "$SIMTOOLS_DIR"
for backend in ${BACKENDS:-sim_telarray obdeect}; do
  dir=$out/$backend; mkdir -p "$dir"
  SECONDS=0; simtools-$app --output_path $dir --ray_tracing_backend $backend \
    --obdeect_seed 11 "$@" > "$dir.log" 2>&1 || echo "FAILED $app $backend"
  echo "$backend: ${SECONDS} s"; tail -1 $dir.log
done
