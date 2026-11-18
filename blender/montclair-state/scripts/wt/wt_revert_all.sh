#!/bin/bash
# wt revert: REVERT_EXACT restores the wr final (sha b66aacdb…99d8; ws made no scene change) from the pre-wt backup.
# Chain: wt -> wr (scripts/wr/wr_revert_all.sh) -> wq -> ...
set -e; cd /workspace/nj-scenes/montclair-state
cp montclair_state_pre_20261108wt.blend montclair_state.blend && sha256sum montclair_state.blend
