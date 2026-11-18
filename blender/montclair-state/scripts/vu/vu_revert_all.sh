#!/bin/bash
# Revert session vu (Blanton door spandrel band cut). Restores pre-vu backup blend (exact),
# or runs in-file REVERT=1 mesh swap. Prefer backup for REVERT_EXACT.
set -e
cd /workspace/nj-scenes/montclair-state
if [[ "${1:-}" == "mesh" ]]; then
  REVERT=1 SAVE=1 /workspace/opt/blender/blender -b montclair_state.blend --python scripts/vu/vu_main.py
else
  if [[ ! -f montclair_state_pre_20261107vu.blend ]]; then
    echo "missing montclair_state_pre_20261107vu.blend" >&2; exit 1
  fi
  cp -f montclair_state_pre_20261107vu.blend montclair_state.blend
  echo "Restored montclair_state_pre_20261107vu.blend -> montclair_state.blend"
  sha256sum montclair_state.blend montclair_state_pre_20261107vu.blend
fi
