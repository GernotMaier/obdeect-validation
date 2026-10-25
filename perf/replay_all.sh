#!/bin/bash
# usage: replay_all.sh <obdeect checkout> <output dir> [--class-b]
# Build reference replay from obdeect main on this machine; never reuse cross-platform .bin files.
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
OBDEECT_DIR=${1:?usage: replay_all.sh <obdeect checkout> <output dir> [--class-b]}
BIN=${2:?}
CLASSB=${3:-}
mkdir -p "$BIN"
tmp=$(mktemp -d)
cleanup() {
  git -C "$OBDEECT_DIR" worktree remove --force "$tmp/reference" >/dev/null 2>&1 || true
  rm -rf "$tmp"
}
trap cleanup EXIT
git -C "$OBDEECT_DIR" worktree add --detach "$tmp/reference" main
"${CXX:-c++}" -std=c++20 -O3 -DNDEBUG -I"$tmp/reference/cpp/include" \
  "$tmp/reference/cpp/bench/replay.cpp" -o "$tmp/replay_ref"
"${CXX:-c++}" -std=c++20 -O3 -DNDEBUG -I"$OBDEECT_DIR/cpp/include" \
  "$OBDEECT_DIR/cpp/bench/replay.cpp" -o "$tmp/replay_new"
PYTHONPATH="$OBDEECT_DIR/python${PYTHONPATH:+:$PYTHONPATH}" \
  python "$HERE/make_models.py"
status=0
for tel in LSTN-01 MSTN-07 MSTS-04 SSTS-17 SCTS-design; do
  "$tmp/replay_ref" write "$HERE/models/$tel.json" "$BIN/$tel.ref.bin"
  "$tmp/replay_new" write "$HERE/models/$tel.json" "$BIN/$tel.new.bin"
  echo "== $tel"
  if [ "$CLASSB" = "--class-b" ]; then
    "$tmp/replay_new" compare --class-b "$BIN/$tel.ref.bin" "$BIN/$tel.new.bin" || status=1
  else
    "$tmp/replay_new" compare "$BIN/$tel.ref.bin" "$BIN/$tel.new.bin" || status=1
  fi
  rm -f "$BIN/$tel.new.bin"
done
exit $status
