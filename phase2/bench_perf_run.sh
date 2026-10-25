#!/bin/bash
# Re-run of the bench.sh star-light cases after the performance work; writes to /tmp/benchperf
# (the committed results in bench/ are not touched).
HERE=$(cd "$(dirname "$0")" && pwd)
RUNS=${RUNS_DIR:-$HERE/runs}
OUT_DIR=${OUT_DIR:-$HERE/bench}
mkdir -p "$OUT_DIR"
python "$HERE/bench_star.py" LSTN-01 "$RUNS/flasher-lstn01/sim_telarray-11/model/7.0.0" > "$OUT_DIR/star-LSTN-01.json"
python "$HERE/bench_star.py" MSTN-07 "$RUNS/flasher-mstn07-nectarcam/sim_telarray-11/model/7.0.0" > "$OUT_DIR/star-MSTN-07.json"
python "$HERE/bench_star.py" MSTS-04 "$RUNS/flasher-msts04-flashcam/sim_telarray-11/model/7.0.0" > "$OUT_DIR/star-MSTS-04.json"
python "$HERE/bench_star.py" SSTS-17 "$RUNS/illuminator-ills03-ssts17/sim_telarray-11/model/7.0.0/ILLS-03_SSTS-17_300nm" > "$OUT_DIR/star-SSTS-17.json"
echo done > "$OUT_DIR/done"
