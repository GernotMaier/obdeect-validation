#!/bin/bash
# R6 stream variant: one matrix cell, route in stream mode (IACT file piped into shower_route, whose output
# is piped into sim_telarray with Bypass_Optics=1, input_file=-). Same inputs, route seed and native seeds as
# run_r6_point.sh (disk mode); the native runs are reused from work/<TEL>_za<ZA>/native_s<seed>.
# Writes work/<TEL>_za<ZA>/route_r6s/ and results/R6-stream_<TEL>_za<ZA>.json (compare.py, route tag r6s).
# usage (container, PYTHONPATH=/workdir/external/wt/simtools-p3/src SITE=North|South): run_r6_stream_point.sh <TEL> <zenith_deg>
set -euo pipefail
TEL=$1; ZA=$2; SEED=${3:-11}
D=/workdir/external/obdeect-validation/phase3
W=$D/work/${TEL}_za${ZA}
R=$W/route_r6s
mkdir -p "$R"
IACT=$W/gamma_${TEL}_za${ZA}.iact
CARD=$(ls "$W"/corsika/run000001/*.input | head -1)
/workdir/env/bin/python $D/scripts/route_setup.py "$TEL" "$ZA" "$R/telescope_map.json" 4242 > "$R/setup.log" 2>&1
MODEL=$W/model/7.0.0
cd "$R"
start=$(date +%s.%N)
cat "$IACT" \
  | /workdir/env/bin/python -m simtools.simtel.shower_route --telescope-map "$R/telescope_map.json" \
      --input - --output - --corsika-card "$CARD" --seed "$SEED" --tracing-seed "$SEED" \
      --simulation-models-path /workdir/external/simulation-models --output-path "$R/export" \
      --ray-tracing-backend obdeect 2> "$R/route.log" \
  | env -u MULTIPIPE_SEQUENTIAL /workdir/simulation_software/sim_telarray/bin/sim_telarray \
      -c "$MODEL/CTAO-${SITE:-South}-$TEL.cfg" -I"$MODEL" \
      -C histogram_file=route.hdata.zst -C random_state=none -C output_file=route.simtel.zst \
      -C random_seed=4242 -C telescope_theta="$ZA" -C telescope_phi=0.0 -C power_law=2.5 \
      -C Bypass_Optics=1 -C show=all - > simtel.log 2>&1
echo "route stream rc=$? wall_s=$(python3 -c "print(round($(date +%s.%N)-$start,1))")" | tee -a "$R/route.log"
/workdir/env/bin/python "$D/scripts/compare.py" "$W" r6s 4242 4243 4244 > "$D/results/R6-stream_${TEL}_za${ZA}.json"
echo "R6 stream done $TEL za$ZA"
