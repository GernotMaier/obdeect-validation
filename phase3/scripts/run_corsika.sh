#!/bin/bash
# CORSIKA-only run (IACT photon bunch file) for one telescope and zenith angle.
# usage: run_corsika.sh <LSTS-01|MSTS-04> <zenith_deg> [showers=50]
# Output: work/<TEL>_za<ZA>/gamma_<TEL>_za<ZA>.iact (decompressed) and work/<TEL>_za<ZA>/model/ (sim_telarray model).
# The container has ~2 GB shared with the production jobs; CORSIKA can be OOM-killed (SIGKILL), so the
# run is retried up to 5 times from scratch.
# Runs inside the container obdeect-val (/workdir/external = repository root).
set -uo pipefail
TEL=$1; ZA=$2; N=${3:-50}
D=/workdir/external/obdeect-validation/phase3
W=$D/work/${TEL}_za${ZA}
mkdir -p "$W"
cd "$W"
ok=0
for attempt in 1 2 3 4 5; do
  rm -rf "$W/corsika" "$W/sub"
  /workdir/env/bin/simtools-simulate-prod --simulation_software corsika --site ${SITE:-South} \
    --array_layout_name "$TEL" --model_version 7.0.0 --primary gamma \
    --zenith_angle "$ZA" --azimuth_angle 0 --energy_range 1 TeV 1 TeV \
    --showers_per_run "$N" --run_number 1 --core_scatter "10 300 m" \
    --corsika_seeds 534 220 1104 382 --corsika_he_interaction qgs3 --corsika_le_interaction urqmd \
    --corsika_path /workdir/simulation_software/corsika7 \
    --corsika_interaction_table_path /workdir/external/corsika7-interaction-tables/interaction-tables \
    --simulation_models_path /workdir/external/simulation-models \
    --output_path "$W" --label "obdv_${TEL}_za${ZA}" > "corsika.stdout.log" 2>&1
  ZST=$(ls "$W"/corsika/run000001/*.corsika.zst 2>/dev/null | head -1)
  if [ -n "$ZST" ] && zstd -q -f -d "$ZST" -o "$W/gamma_${TEL}_za${ZA}.iact" 2>/dev/null; then
    ok=1; break
  fi
  echo "attempt $attempt failed for $TEL za$ZA" >&2
done
[ "$ok" = 1 ] || { echo "CORSIKA failed for $TEL za$ZA" >&2; exit 1; }
echo "done $TEL za$ZA showers=$N attempt=$attempt iact=$W/gamma_${TEL}_za${ZA}.iact"
