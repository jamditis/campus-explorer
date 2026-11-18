#!/bin/bash
# revert test on a copy INSIDE montclair-state/ (linked libs are relative); state jsons are backed up and restored
cd /workspace/nj-scenes/montclair-state; B=/workspace/opt/blender/blender; C=montclair_state_reverttest_oi.blend
cp montclair_state.blend $C; cp data/oi/oi_state.json /tmp/oi_state.bak; cp data/oi/oi_wing_state.json /tmp/oi_wing_state.bak
for s in oi_cam oi_wing oi_pavilion; do REVERT=1 $B -b $C --python scripts/oi/$s.py -- --save 2>&1 | grep -E "REVERTED|SAVED|Error|Trace"; done
cp /tmp/oi_state.bak data/oi/oi_state.json; cp /tmp/oi_wing_state.bak data/oi/oi_wing_state.json
for f in $C montclair_state_pre_20261031oi.blend; do echo $f; $B -b $f --python scripts/oi/oi_sig.py 2>&1 | grep SIG; done
rm -f $C ${C}1
