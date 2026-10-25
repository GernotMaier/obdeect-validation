#!/bin/bash
# usage: bench_all.sh <bench_trace binary>
cd "$(dirname "$0")"
B=$1
echo "== LSTN-01";     $B models/LSTN-01.json 14.745459896975749 -0.9325 28.133
echo "== MSTN-07";     $B models/MSTN-07.json 8.1696 1.775 18.8005
echo "== MSTS-04";     $B models/MSTS-04.json 8.1696 1.775 19.575
echo "== SSTS-17";     $B models/SSTS-17.json 2.5446 0.0 4.1084
echo "== SCTS-design"; $B models/SCTS-design.json 5.79828 2.03 11.40945
