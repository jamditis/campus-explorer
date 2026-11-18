#!/bin/bash
# sf revert: BLEND (default montclair_state.blend) -> pre-sf state (removes SF lot/road/footways/stripes/containers + SF cams + asphalt material,
# restores the 3 culled grass meshes from montclair_state_pre_20261104sf.blend, puts RZ_CAM_eye_SC_from_E back). Saves in place.
cd /workspace/nj-scenes/montclair-state; B=/workspace/opt/blender/blender; F=${BLEND:-montclair_state.blend}
REVERT=1 SAVE=1 $B -b $F --python scripts/sf/sf_detail.py 2>&1 | grep -E "SAVED|Error"
REVERT=1 SAVE=1 $B -b $F --python scripts/sf/sf_lot.py 2>&1 | grep -E "SF |SAVED|Error"
