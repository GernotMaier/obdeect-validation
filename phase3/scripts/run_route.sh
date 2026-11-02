#!/bin/bash
# obdeect route: IACT file -> camera photon bunches (shower_route CLI), then sim_telarray with Bypass_Optics=1.
# usage: run_route.sh <LSTS-01|MSTS-04> <zenith_deg> <route_seed> <tag>
# Needs work/<TEL>_za<ZA>/ from run_corsika.sh. Outputs in work/<TEL>_za<ZA>/route_<tag>/.
set -euo pipefail
TEL=$1; ZA=$2; SEED=$3; TAG=$4
D=/workdir/external/obdeect-validation/phase3
W=$D/work/${TEL}_za${ZA}
R=$W/route_$TAG
mkdir -p "$R"
IACT=$W/gamma_${TEL}_za${ZA}.iact
/workdir/env/bin/python $D/scripts/route_setup.py "$TEL" "$ZA" "$R/telescope_map.json" 4242 > "$R/setup.log" 2>&1
cat "$R/setup.log"
# optional override of the input-plane height (m), used when the route guard rejects the minimum-height rounding
if [ -n "${ROUTE_HEIGHT_OVERRIDE:-}" ]; then
  /workdir/env/bin/python -c "import json,sys; p=sys.argv[1]; m=json.load(open(p)); m['0']['input_plane_height_m']=float(sys.argv[2]); json.dump(m, open(p,'w'), indent=1)" "$R/telescope_map.json" "$ROUTE_HEIGHT_OVERRIDE"
  echo "input_plane_height_m overridden to $ROUTE_HEIGHT_OVERRIDE"
fi
MODEL=$W/model/7.0.0
CARD=$(ls "$W"/corsika/run000001/*.input | head -1)  # CORSIKA card: CSCAT (core reuses) sets the blocks per shower
start=$(date +%s.%N)
/workdir/env/bin/python -m simtools.simtel.shower_route --telescope-map "$R/telescope_map.json" \
  --input "$IACT" --corsika-card "$CARD" --output "$R/bunches.iact" --seed "$SEED" --tracing-seed "$SEED" \
  --simulation-models-path /workdir/external/simulation-models --output-path "$R/export" \
  > "$R/route.log" 2>&1
echo "route wall_s=$(python3 -c "print(round($(date +%s.%N)-$start,1))")" | tee -a "$R/route.log"
cd "$R"
/workdir/simulation_software/sim_telarray/bin/sim_telarray -c "$MODEL/CTAO-${SITE:-South}-$TEL.cfg" -I"$MODEL" \
  -C histogram_file=route.hdata.zst -C random_state=none -C output_file=route.simtel.zst \
  -C random_seed=4242 -C telescope_theta="$ZA" -C telescope_phi=0.0 -C power_law=2.5 \
  -C Bypass_Optics=1 -C input_file="$R/bunches.iact" > simtel.log 2>&1
echo "route sim_telarray rc=$?"
