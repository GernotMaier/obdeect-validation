#!/bin/bash
# Incident angles with both backends. Usage: incident.sh site tel off
SIMTOOLS_DIR=${SIMTOOLS_DIR:-/workdir/external/simtools}
OUT_DIR=${OUT_DIR:-$(cd "$(dirname "$0")" && pwd)/runs/incident${TAG}}
case "$OUT_DIR" in /*) ;; *) OUT_DIR=$PWD/$OUT_DIR ;; esac
cd "$SIMTOOLS_DIR"
for b in sim_telarray obdeect; do
  d=$OUT_DIR/$2/$b; mkdir -p "$d"
  simtools-derive-incident-angle --site $1 --telescope $2 --model_version 6.0.2 --off_axis_angles $3 \
    --number_of_photons ${NPH:-200000} --zenith_angle 20 --output_path $d --ray_tracing_backend $b \
    --obdeect_seed 5 --parameter_version 1.0.0 > "$d.log" 2>&1 || echo "FAIL $2 $b"
done
