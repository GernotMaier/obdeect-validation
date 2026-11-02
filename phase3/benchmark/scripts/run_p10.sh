#!/bin/bash
# usage: run_p10.sh <block> [<block> ...]   (host driver; load snapshot before and after each block)
# Blocks run inside the container obdeect-val through scripts/run_block.py; results in results/.
D="$(cd "$(dirname "$0")/.." && pwd)"
C=/workdir/external/obdeect-validation/phase3/benchmark
for b in "$@"; do
  "$D/scripts/snap.sh" "before $b" "$D/results/load.log"
  echo "### $b start $(date -u +%FT%TZ)"
  podman exec obdeect-val /workdir/env/bin/python "$C/scripts/run_block.py" "$b" > "$D/results/$b.stdout" 2>&1
  echo "### $b rc=$? end $(date -u +%FT%TZ)"
  "$D/scripts/snap.sh" "after $b" "$D/results/load.log"
done
