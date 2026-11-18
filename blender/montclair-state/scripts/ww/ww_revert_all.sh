#!/bin/bash
# ww REVERT_EXACT: restore the pre-ww main (= wv, sha 32197c1ae4e54a6a27e375a028365b203890772f6e3e7a84a17e3de0b7d30405)
set -e
R=/workspace/nj-scenes/montclair-state
cp "$R/montclair_state_pre_20261108ww.blend" "$R/montclair_state.blend"
sha256sum "$R/montclair_state.blend"
echo "expected 32197c1ae4e54a6a27e375a028365b203890772f6e3e7a84a17e3de0b7d30405 (wv). Docs: restore data/ww/STATE_pre_ww.md / PLAN_pre_ww.md / LOG_pre_ww.md by hand if wanted."
