#!/bin/bash
# Matched ray tracing with the obdeect backend, for comparison with val/psf-6.0.2 (container).
# Usage: validate_run.sh <out> <site:telescope>...
out=$1; shift
SIMTOOLS_DIR=${SIMTOOLS_DIR:-/workdir/external/simtools}
case "$out" in /*) ;; *) out=$PWD/$out ;; esac
cd "$SIMTOOLS_DIR"
for spec in "$@"; do
  site=${spec%%:*}; tel=${spec##*:}
  dir=$out/$tel/obdeect
  mkdir -p $dir
  simtools-validate-optics --site $site --telescope $tel --model_version 6.0.2 \
    --zenith_angle 20 --source_distance 10 --max_offset 4 --offset_step 1 \
    --offset_directions N,E --output_path $dir --ray_tracing_backend obdeect \
    --instrument_seed 11 --simulation_seed 11 > $dir.log 2>&1 || echo "FAILED $tel"
done
echo done
