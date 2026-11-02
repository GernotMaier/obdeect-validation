#!/bin/bash
# North points added by the coordinator scope: LSTN-01 and MSTN-07, zenith 20 and 60 deg (40 deg after).
D=/workdir/external/obdeect-validation/phase3
export SITE=North
for ZA in 20 60 40; do
  for TEL in LSTN-01 MSTN-07; do
    "$D/scripts/run_point.sh" "$TEL" "$ZA" 50
    echo "NORTH $TEL $ZA exit=$? $(date)" >> "$D/work/north.log"
  done
done
echo "NORTH DONE $(date)" >> "$D/work/north.log"
