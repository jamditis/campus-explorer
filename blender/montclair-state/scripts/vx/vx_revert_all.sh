#!/usr/bin/env bash
# REVERT_EXACT: restore pre-vx backup over MAIN.
set -euo pipefail
ROOT=/workspace/nj-scenes/montclair-state
SRC=$ROOT/montclair_state_pre_20261107vx.blend
DST=$ROOT/montclair_state.blend
[[ -f "$SRC" ]] || { echo "missing backup $SRC" >&2; exit 1; }
cp -f "$SRC" "$DST"; echo "restored $SRC -> $DST"; sha256sum "$DST"
