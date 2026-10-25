#!/bin/bash
# Benchmark and replay check of obdeect on production hardware (x86-64 Linux).
#
# Usage:
#   bash bench_hw.sh <obdeect repo> <out dir> 2>&1 | tee <out dir>/bench_hw.log
#
#   <obdeect repo>  the obdeect checkout to build (cpp/include, cpp/bench)
#   <out dir>       new directory for binaries, benchmark output and replay results
#
# What it does:
#   1. prints lscpu and the compiler version;
#   2. builds bench_trace and replay twice: -O3, and -O3 -march=x86-64-v3,
#      both with -ffp-contract=off (no FMA contraction, so the two builds
#      must agree bit for bit);
#   3. runs bench_all.sh with each build (bench_o3.txt, bench_march.txt);
#   4. writes the replay files of all five models with both builds and
#      compares them (replay compare must print IDENTICAL). Identical pairs
#      are deleted; the .bin files are about 0.5 GB each, so keep disk space
#      free for one model at a time.
#
# Exit status: 0 if all replay comparisons are identical, 1 otherwise.
# Run on an otherwise idle node; the timings are only meaningful then.
# Needs a C++20 compiler (c++ or $CXX) and bash.

set -euo pipefail

HERE=$(cd "$(dirname "$0")" && pwd)
OBDEECT=${1:?usage: bench_hw.sh <obdeect repo> <out dir>}
OUT=${2:?usage: bench_hw.sh <obdeect repo> <out dir>}
CXX=${CXX:-c++}
MODELS="LSTN-01 MSTN-07 MSTS-04 SSTS-17 SCTS-design"

if [ -e "$OUT" ]; then
  echo "out dir exists: $OUT" >&2
  exit 2
fi
mkdir -p "$OUT"

echo "== host"
uname -a
lscpu
echo "== compiler"
"$CXX" --version | head -n 1
echo

build() {
  local name=$1
  shift
  local dir="$OUT/build-$name"
  mkdir -p "$dir"
  for tool in bench_trace replay; do
    echo "== build $name: $tool ($*)"
    "$CXX" -std=c++20 -DNDEBUG -ffp-contract=off "$@" \
      -I"$OBDEECT/cpp/include" "$OBDEECT/cpp/bench/$tool.cpp" -o "$dir/$tool"
  done
}

build o3 -O3
build march -O3 -march=x86-64-v3

echo "== bench_all: -O3"
"$HERE/bench_all.sh" "$OUT/build-o3/bench_trace" | tee "$OUT/bench_o3.txt"
echo "== bench_all: -O3 -march=x86-64-v3"
"$HERE/bench_all.sh" "$OUT/build-march/bench_trace" | tee "$OUT/bench_march.txt"

status=0
echo "== replay: -O3 against -O3 -march=x86-64-v3"
for tel in $MODELS; do
  "$OUT/build-o3/replay" write "$HERE/models/$tel.json" "$OUT/$tel.o3.bin"
  "$OUT/build-march/replay" write "$HERE/models/$tel.json" "$OUT/$tel.march.bin"
  echo "== $tel"
  if "$OUT/build-o3/replay" compare "$OUT/$tel.o3.bin" "$OUT/$tel.march.bin"; then
    rm -f "$OUT/$tel.o3.bin" "$OUT/$tel.march.bin"
  else
    status=1
  fi
done

if [ "$status" -eq 0 ]; then
  echo "== replay: all five models IDENTICAL between the two builds"
else
  echo "== replay: DIFFERENT for at least one model (files kept in $OUT)"
fi
exit "$status"
