#!/bin/bash
# Runs the full matrix in the order 20 deg, 60 deg, 40 deg (20 and 60 first, as planned), both telescopes.
D=/workdir/external/obdeect-validation/phase3
for ZA in 20 60 40; do
  for TEL in LSTS-01 MSTS-04; do
    "$D/scripts/run_point.sh" "$TEL" "$ZA" 50
  done
done
echo "MATRIX DONE $(date)" >> "$D/work/matrix.log"
