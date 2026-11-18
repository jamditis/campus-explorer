#!/usr/bin/env bash
# REVERT_EXACT: restore pre-vv backup over MAIN (also restores TJ grass verts).
set -euo pipefail
ROOT=/workspace/nj-scenes/montclair-state
SRC=$ROOT/montclair_state_pre_20261107vv.blend
DST=$ROOT/montclair_state.blend
if [[ ! -f "$SRC" ]]; then
  echo "missing backup $SRC" >&2; exit 1
fi
cp -f "$SRC" "$DST"
echo "restored $SRC -> $DST"
sha256sum "$DST"
