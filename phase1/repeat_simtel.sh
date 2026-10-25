#!/bin/bash
# Repeated on-axis sim_telarray runs: effective area spread. Usage: repeat_simtel.sh site tel version n
SIMTOOLS_DIR=${SIMTOOLS_DIR:-/workdir/external/simtools}
OUT_DIR=${OUT_DIR:-$(cd "$(dirname "$0")" && pwd)/runs/repeat}
case "$OUT_DIR" in /*) ;; *) OUT_DIR=$PWD/$OUT_DIR ;; esac
cd "$SIMTOOLS_DIR"
for i in $(seq 1 $4); do
  d=$OUT_DIR/$2/run$i
  mkdir -p "$d"
  simtools-validate-optics --site $1 --telescope $2 --model_version $3 --zenith_angle 20 \
    --source_distance 10 --max_offset 0 --offset_step 1 --output_path $d \
    --ray_tracing_backend sim_telarray > "$d.log" 2>&1 || echo FAILED $i
  grep -v "^#" $d/results/*.ecsv | sed -n 2p | awk '{print "run '$i'", $6}'
done
