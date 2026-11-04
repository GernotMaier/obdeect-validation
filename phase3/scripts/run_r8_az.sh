#!/bin/bash
# R8: MSTS-04 at shower azimuth AZ (phi != 0): own CORSIKA IACT run at azimuth AZ, model export, natives (seeds
# 4242-4244) and route (seed 11) with telescope_phi = AZ and map phi_deg = AZ, then compare.py and per-event times.
# Writes results/R8_<TEL>_za<ZA>_az<AZ>.json and results/R8_times_<TEL>_za<ZA>_az<AZ>.json.
# usage (container, PYTHONPATH=<worktree>/src, SITE=South): run_r8_az.sh <TEL> <zenith_deg> <azimuth_deg>
set -uo pipefail
TEL=$1; ZA=$2; AZ=$3
D=/workdir/external/obdeect-validation/phase3
W=$D/work/${TEL}_za${ZA}_az${AZ}
mkdir -p "$W"
exec >> "$W/r8.log" 2>&1
echo "=== $(date) R8 start $TEL za$ZA az$AZ site ${SITE:-South}"
if [ ! -s "$W/gamma_${TEL}_za${ZA}.iact" ]; then "$D/scripts/run_corsika_az.sh" "$TEL" "$ZA" "$AZ" 50 || exit 1; fi
MODEL=$W/model/7.0.0
# the telescope model does not depend on the shower azimuth: reuse the za point's exported model
[ -e "$W/model" ] || ln -s "$D/work/${TEL}_za${ZA}/model" "$W/model"
[ -f "$MODEL/CTAO-${SITE:-South}-$TEL.cfg" ] || { echo "model missing: $MODEL"; exit 1; }
for s in 4242 4243 4244; do
  mkdir -p "$W/native_s$s"; cd "$W/native_s$s"
  /workdir/simulation_software/sim_telarray/bin/sim_telarray -c "$MODEL/CTAO-${SITE:-South}-$TEL.cfg" -I"$MODEL" \
    -C histogram_file=native.hdata.zst -C random_state=none -C output_file=native.simtel.zst \
    -C random_seed="$s" -C telescope_theta="$ZA" -C telescope_phi="$AZ" -C power_law=2.5 \
    -C Bypass_Optics=0 -C input_file="$W/gamma_${TEL}_za${ZA}.iact" > simtel.log 2>&1
  echo "native seed $s rc=$?"
done
R=$W/route_r8
mkdir -p "$R"
/workdir/env/bin/python $D/scripts/route_setup.py "$TEL" "$ZA" "$R/telescope_map.json" 4242 > "$R/setup.log" 2>&1
/workdir/env/bin/python -c "import json,sys; p=sys.argv[1]; m=json.load(open(p)); m['0']['phi_deg']=float(sys.argv[2]); json.dump(m, open(p,'w'), indent=1)" "$R/telescope_map.json" "$AZ"
CARD=$(ls "$W"/corsika/run000001/*.input | head -1)
/workdir/env/bin/python -m simtools.simtel.shower_route --telescope-map "$R/telescope_map.json" \
  --input "$W/gamma_${TEL}_za${ZA}.iact" --corsika-card "$CARD" --output "$R/bunches.iact" --seed 11 --tracing-seed 11 \
  --simulation-models-path /workdir/external/simulation-models --output-path "$R/export" > "$R/route.log" 2>&1
echo "route rc=$?"
cd "$R"
/workdir/simulation_software/sim_telarray/bin/sim_telarray -c "$MODEL/CTAO-${SITE:-South}-$TEL.cfg" -I"$MODEL" \
  -C histogram_file=route.hdata.zst -C random_state=none -C output_file=route.simtel.zst \
  -C random_seed=4242 -C telescope_theta="$ZA" -C telescope_phi="$AZ" -C power_law=2.5 \
  -C Bypass_Optics=1 -C input_file="$R/bunches.iact" > simtel.log 2>&1
echo "route sim_telarray rc=$?"
/workdir/env/bin/python "$D/scripts/compare.py" "$W" r8 4242 4243 4244 > "$D/results/R8_${TEL}_za${ZA}_az${AZ}.json"
/workdir/env/bin/python "$D/scripts/per_event_times.py" "$W" r8 4242 > "$D/results/R8_times_${TEL}_za${ZA}_az${AZ}.json"
echo "=== $(date) R8 done $TEL za$ZA az$AZ"
