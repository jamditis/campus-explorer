#!/bin/bash
# wu revert: REVERT_EXACT restores the wt final (sha 40f9957c…36ab) from the pre-wu backup.
# Chain: wu -> wt -> wr (scripts/wt/wt_revert_all.sh) -> wq -> ...
set -e; cd /workspace/nj-scenes/montclair-state
cp montclair_state_pre_20261108wu.blend montclair_state.blend && sha256sum montclair_state.blend
