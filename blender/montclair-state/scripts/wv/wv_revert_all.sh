#!/bin/bash
# wv revert: REVERT_EXACT restores the wu final (sha 1cf6623e…57a5) from the pre-wv backup.
# Chain: wv -> wu (scripts/wu/wu_revert_all.sh) -> wt -> ...
set -e; cd /workspace/nj-scenes/montclair-state
cp montclair_state_pre_20261108wv.blend montclair_state.blend && sha256sum montclair_state.blend
