#!/bin/bash
# wy REVERT_EXACT: restore the pre-wy main (= wx, sha 1f78db55dc840108d1719c0f548f403ba204e757ae02d47d29c4f2fdf346d365)
set -e
R=/workspace/nj-scenes/montclair-state
cp "$R/montclair_state_pre_20261108wy.blend" "$R/montclair_state.blend"
sha256sum "$R/montclair_state.blend"
echo "expected 1f78db55dc840108d1719c0f548f403ba204e757ae02d47d29c4f2fdf346d365 (wx)"
