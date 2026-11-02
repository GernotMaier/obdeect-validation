#!/bin/bash
# Native sim_telarray on the CORSIKA IACT file (Bypass_Optics=0, full optics).
# usage: run_native.sh <LSTS-01|MSTS-04> <zenith_deg> <sim_telarray_seed> <tag>
set -euo pipefail
TEL=$1; ZA=$2; SEED=$3; TAG=$4
D=/workdir/external/obdeect-validation/phase3
W=$D/work/${TEL}_za${ZA}
N=$W/native_$TAG
mkdir -p "$N"
MODEL=$W/model/7.0.0
cd "$N"
/workdir/simulation_software/sim_telarray/bin/sim_telarray -c "$MODEL/CTAO-${SITE:-South}-$TEL.cfg" -I"$MODEL" \
  -C histogram_file=native.hdata.zst -C random_state=none -C output_file=native.simtel.zst \
  -C random_seed="$SEED" -C telescope_theta="$ZA" -C telescope_phi=0.0 -C power_law=2.5 \
  -C Bypass_Optics=0 -C input_file="$W/gamma_${TEL}_za${ZA}.iact" > simtel.log 2>&1
echo "native sim_telarray rc=$?"
