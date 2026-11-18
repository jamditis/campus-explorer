#!/usr/bin/env bash
# REVERT_EXACT: restore pre-wa backup (= vz final 0cdea497…5231dab9) over MAIN.
set -euo pipefail
ROOT=/workspace/nj-scenes/montclair-state
SRC=$ROOT/montclair_state_pre_20261107wa.blend
DST=$ROOT/montclair_state.blend
[[ -f "$SRC" ]] || { echo "missing backup $SRC" >&2; exit 1; }
cp -f "$SRC" "$DST"; echo "restored $SRC -> $DST"; sha256sum "$DST"
