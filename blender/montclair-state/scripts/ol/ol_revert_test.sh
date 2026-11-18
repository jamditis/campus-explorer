#!/bin/bash
cd /workspace/nj-scenes/montclair-state; B=/workspace/opt/blender/blender; T=ol_revert_test.blend
cp montclair_state.blend $T
for s in ol_islands ol_cam ol_build; do REVERT=1 $B -b $T --python scripts/ol/$s.py -- --save 2>&1 | grep -E "REVERTED|SAVED|Error|Trace"; done
$B -b $T --python scripts/oj/oj_sig.py -- data/ol/sig_reverted.json 2>&1 | grep SIG
$B -b montclair_state_pre_20261031ol.blend --python scripts/oj/oj_sig.py -- data/ol/sig_backup.json 2>&1 | grep SIG
cmp data/ol/sig_reverted.json data/ol/sig_backup.json && echo REVERT MATCH || { echo REVERT DIFF; diff data/ol/sig_reverted.json data/ol/sig_backup.json | head; }
cat > /tmp/ol_smooth.py <<'P'
import bpy; o=bpy.data.objects['OK_Schmitt_entrance_walk_lawn_embankment']; print('SMOOTHCOUNT',sum(p.use_smooth for p in o.data.polygons),len(bpy.data.objects))
P
$B -b $T --python /tmp/ol_smooth.py 2>&1 | grep SMOOTHCOUNT; $B -b montclair_state_pre_20261031ol.blend --python /tmp/ol_smooth.py 2>&1 | grep SMOOTHCOUNT
rm -f $T ${T}1
