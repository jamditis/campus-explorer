#!/usr/bin/env bash
# REVERT_EXACT: restore pre-wi backup (session wh state c92801d5…92b33a2)
set -euo pipefail
cd /workspace/nj-scenes/montclair-state
test -f montclair_state_pre_20261107wi.blend
cp -f montclair_state_pre_20261107wi.blend montclair_state.blend
echo "REVERT_EXACT restored montclair_state_pre_20261107wi.blend"
sha256sum montclair_state.blend | cut -c1-64
