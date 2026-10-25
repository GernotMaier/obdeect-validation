#!/bin/bash
# Matched ray tracing: simtools-validate-optics with both backends.
# Usage: run_psf.sh <out> <model_version> <site:telescope>... [-- extra args]
out=${1:?usage: run_psf.sh <out> <model_version> <site:telescope>...}; version=${2:?}; shift 2
HERE=$(cd "$(dirname "$0")" && pwd)
SIMTOOLS_DIR=${SIMTOOLS_DIR:-/workdir/external/simtools}
CALLER_DIR=$PWD
OUT_DIR=${OUT_DIR:-$out}
case "$OUT_DIR" in
  /*) ;;
  *) OUT_DIR=$CALLER_DIR/$OUT_DIR ;;
esac
mkdir -p "$OUT_DIR"
cd "$SIMTOOLS_DIR"
status=0
for spec in "$@"; do
  site=${spec%%:*}; tel=${spec##*:}
  for backend in ${BACKENDS:-sim_telarray obdeect}; do
    dir=$OUT_DIR/$tel/$backend
    mkdir -p "$dir"
    compgen -G "$dir/results/*.ecsv" >/dev/null && continue
    simtools-validate-optics --site $site --telescope $tel --model_version $version \
      --zenith_angle 20 --source_distance 10 --max_offset 4 --offset_step 1 \
      --offset_directions N,E --output_path $dir --ray_tracing_backend $backend \
      --instrument_seed 11 --simulation_seed 11 > "$dir.log" 2>&1 || {
        echo "FAILED $tel $backend"
        status=1
      }
  done
done
echo done
exit "$status"
