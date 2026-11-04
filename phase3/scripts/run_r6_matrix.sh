#!/bin/bash
# R6 matrix driver: one lane per site (run in parallel, 2 lanes to fit the 2 GB container).
# usage (container): run_r6_matrix.sh <South|North>
D=/workdir/external/obdeect-validation/phase3
export PYTHONPATH=/workdir/external/wt/simtools-p3/src
export SITE=$1
if [ "$SITE" = South ]; then TELS="LSTS-01 MSTS-04"; else TELS="LSTN-01 MSTN-07"; fi
for ZA in 20 40 60; do
  for TEL in $TELS; do
    "$D/scripts/run_r6_point.sh" "$TEL" "$ZA" 50
    echo "R6 $SITE $TEL $ZA exit=$? $(date)" >> "$D/work/r6_matrix_$SITE.log"
  done
done
echo "R6 $SITE MATRIX DONE $(date)" >> "$D/work/r6_matrix_$SITE.log"
