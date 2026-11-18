#!/bin/bash
# sd revert: BLEND (default montclair_state.blend) -> pre-sd state (bed coords, letters mesh, camera). Saves in place.
cd /workspace/nj-scenes/montclair-state; B=/workspace/opt/blender/blender; F=${BLEND:-montclair_state.blend}
REVERT=1 SAVE=1 $B -b $F --python scripts/sd/sd_bed.py 2>&1 | grep -E "SD_|SAVED"
REVERT=1 SAVE=1 $B -b $F --python scripts/sd/sd_letters.py 2>&1 | grep -E "SD_|SAVED"
REVERT=1 SAVE=1 $B -b $F --python scripts/sd/sd_cam.py 2>&1 | grep -E "SD_|SAVED"
