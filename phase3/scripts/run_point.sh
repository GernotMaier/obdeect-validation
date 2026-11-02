#!/bin/bash
# Full chain for one telescope and zenith: CORSIKA-only IACT, 3 native seeds, route (seed 11), route repeat
# (determinism), comparison. usage: run_point.sh <LSTS-01|MSTS-04> <zenith_deg> [showers=50]
set -uo pipefail
TEL=$1; ZA=$2; N=${3:-50}
D=/workdir/external/obdeect-validation/phase3
W=$D/work/${TEL}_za${ZA}
LOG=$W/point.log
exec >> "$LOG" 2>&1
echo "=== $(date) start $TEL za$ZA showers $N"
if [ ! -s "$W/gamma_${TEL}_za${ZA}.iact" ]; then "$D/scripts/run_corsika.sh" "$TEL" "$ZA" "$N" || exit 1; fi
if [ ! -f "$W/model/7.0.0/CTAO-${SITE:-South}-$TEL.cfg" ]; then /workdir/env/bin/python "$D/scripts/export_model.py" "$TEL" "$W" || exit 1; fi
for s in 4242 4243 4244; do "$D/scripts/run_native.sh" "$TEL" "$ZA" "$s" "s$s"; done
"$D/scripts/run_route.sh" "$TEL" "$ZA" 11 r11
"$D/scripts/run_route.sh" "$TEL" "$ZA" 11 r11rep
/workdir/env/bin/python "$D/scripts/determinism.py" "$W" r11 r11rep > "$W/determinism.json"
/workdir/env/bin/python "$D/scripts/compare.py" "$W" r11 4242 4243 4244 > "$D/results/${TEL}_za${ZA}.json"
echo "=== $(date) done"
