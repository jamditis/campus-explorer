#!/bin/bash
cd /workspace/nj-scenes/montclair-state; B=/workspace/opt/blender/blender; T=or_revert_test.blend
cp montclair_state.blend $T
REVERT=1 $B -b $T --python scripts/or/or_build.py -- --save 2>&1 | grep -E "REVERTED|OQ_REBUILT|SAVED|Error|Trace|WIN|EAST"
$B -b $T --python scripts/oj/oj_sig.py -- data/or/sig_reverted.json 2>&1 | grep SIG
$B -b montclair_state_pre_20261031or.blend --python scripts/oj/oj_sig.py -- data/or/sig_backup.json 2>&1 | grep SIG
cmp data/or/sig_reverted.json data/or/sig_backup.json && echo REVERT MATCH || { echo REVERT DIFF; diff data/or/sig_reverted.json data/or/sig_backup.json | head; }
REVERT=1 $B -b $T --python scripts/or/or_cam.py -- --save 2>&1 | grep -E "REVERTED|Error"; $B -b $T --python scripts/oj/oj_sig.py -- data/or/sig_reverted2.json 2>&1 | grep SIG; cmp data/or/sig_reverted2.json data/or/sig_backup.json && echo REVERT2 MATCH
cat > /tmp/or_x.py <<'Q'
import bpy, hashlib
out=[]
for o in sorted(bpy.data.objects,key=lambda o:o.name):
    if o.name.startswith(('OQ_skirt_win','OR_')): me=o.data; out.append((o.name,len(me.vertices),hashlib.sha1(b''.join(('%.4f%.4f%.4f'%tuple(v.co)).encode() for v in me.vertices)).hexdigest()[:10],[m.name for m in me.materials]))
fp=bpy.data.objects['Footpaths_OSM'].material_slots[0]; print('XCHK',out,fp.link,fp.material.name)
Q
$B -b $T --python /tmp/or_x.py 2>&1 | grep XCHK; $B -b montclair_state_pre_20261031or.blend --python /tmp/or_x.py 2>&1 | grep XCHK
rm -f $T ${T}1
