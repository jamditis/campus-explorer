#!/bin/bash
# wx REVERT_EXACT: restore the pre-wx main (= ww, sha 1588c59454c825a11f39208f11c0f0fb9842f148c13fddc4e8ac266361b43913)
set -e
R=/workspace/nj-scenes/montclair-state
cp "$R/montclair_state_pre_20261108wx.blend" "$R/montclair_state.blend"
sha256sum "$R/montclair_state.blend"
echo "expected 1588c59454c825a11f39208f11c0f0fb9842f148c13fddc4e8ac266361b43913 (ww)"
