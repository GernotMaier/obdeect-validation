#!/bin/bash
# validate-cumulative-psf for LSTN-01 with the obdeect backend (container). Usage: cumpsf_run.sh <out>
out=$1
SIMTOOLS_DIR=${SIMTOOLS_DIR:-/workdir/external/simtools}
case "$out" in /*) ;; *) out=$PWD/$out ;; esac
cd "$SIMTOOLS_DIR"
mkdir -p $out
simtools-validate-cumulative-psf --site North --telescope LSTN-01 --model_version 6.0.2 \
  --zenith_angle 20 --source_distance 10 --data "$DATA" --ray_tracing_backend obdeect \
  --instrument_seed 11 --simulation_seed 11 --output_path $out > $out.log 2>&1 || echo FAILED
echo done
