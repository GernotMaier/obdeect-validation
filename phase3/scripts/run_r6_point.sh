#!/bin/bash
# R6 rerun (2026-11-03): one matrix cell with the current code. Same CORSIKA IACT input, native seeds 4242-4244,
# route seed 11 (disk mode: shower_route CLI, then sim_telarray Bypass_Optics=1), route repeat (determinism).
# Writes results/R6_<TEL>_za<ZA>.json (the earlier results/<TEL>_za<ZA>.json are kept).
# usage (container, PYTHONPATH=/workdir/external/wt/simtools-p3/src SITE=North|South): run_r6_point.sh <TEL> <zenith_deg> [showers=50]
set -uo pipefail
TEL=$1; ZA=$2; N=${3:-50}
D=/workdir/external/obdeect-validation/phase3
W=$D/work/${TEL}_za${ZA}
exec >> "$W/r6.log" 2>&1
echo "=== $(date) R6 start $TEL za$ZA site ${SITE:-South} PYTHONPATH=$PYTHONPATH"
if [ ! -s "$W/gamma_${TEL}_za${ZA}.iact" ]; then "$D/scripts/run_corsika.sh" "$TEL" "$ZA" "$N" || exit 1; fi
for s in 4242 4243 4244; do "$D/scripts/run_native.sh" "$TEL" "$ZA" "$s" "s$s"; done
"$D/scripts/run_route.sh" "$TEL" "$ZA" 11 r6
"$D/scripts/run_route.sh" "$TEL" "$ZA" 11 r6rep
/workdir/env/bin/python "$D/scripts/determinism.py" "$W" r6 r6rep > "$W/determinism_r6.json"
/workdir/env/bin/python "$D/scripts/compare.py" "$W" r6 4242 4243 4244 > "$D/results/R6_${TEL}_za${ZA}.json"
echo "=== $(date) R6 done $TEL za$ZA rc=$?"
