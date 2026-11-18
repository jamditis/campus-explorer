#!/bin/bash
# wz REVERT_EXACT: restore the pre-wz main (= wy, sha 64f33d7bff70c75bd6b2935c08f872fc637ac2fbb7e84ec6bc9495d9e6ff2051)
set -e
R=/workspace/nj-scenes/montclair-state
cp "$R/montclair_state_pre_20261108wz.blend" "$R/montclair_state.blend"
sha256sum "$R/montclair_state.blend"
echo "expected 64f33d7bff70c75bd6b2935c08f872fc637ac2fbb7e84ec6bc9495d9e6ff2051 (wy)"
