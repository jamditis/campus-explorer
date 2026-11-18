#!/bin/bash
# sg revert: BLEND (default montclair_state.blend) -> pre-sg state (removes SG roads/curbs/stains/cams + materials, restores the lot,
# SF footway and grass meshes from their fake-user originals, un-hides the sf Quad Road ribbon, puts the sf stripe material back). Saves in place.
cd /workspace/nj-scenes/montclair-state; B=/workspace/opt/blender/blender; F=${BLEND:-montclair_state.blend}
REVERT=1 SAVE=1 $B -b $F --python scripts/sg/sg_main.py 2>&1 | grep -E "SG |SAVED|Error"
