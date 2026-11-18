#!/bin/bash
# revert test on a copy INSIDE montclair-state/ (linked libs are relative)
cd /workspace/nj-scenes/montclair-state; B=/workspace/opt/blender/blender; C=montclair_state_reverttest_oh.blend
cp montclair_state.blend $C
for s in oh_deck oh_roof3 oh_roof2 oh_downspouts oh_entrance oh_landing oh_doorcut oh_cam oh_build; do REVERT=1 $B -b $C --python scripts/oh/$s.py -- --save 2>&1 | grep -E "REVERTED|SAVED|Error|Trace"; done
cat > /tmp/oh_count.py <<'PY'
import bpy
w=bpy.data.objects['Schmitt Hall walls']; r=bpy.data.objects['Schmitt Hall roof (LiDAR)']
print('COUNT',len(bpy.context.scene.objects),len(bpy.data.objects),'wallfaces',len(w.data.polygons),'wallmat',[m.name for m in w.data.materials],'roofattrs',sorted(a.name for a in r.data.attributes if not a.name.startswith('.')),'OHmats',sorted(m.name for m in bpy.data.materials if m.name.startswith('OH_')),'roofnodes',len(bpy.data.materials['Roof_tile_or_membrane'].node_tree.nodes),len(bpy.data.materials['Roof_tile_or_membrane'].node_tree.links),'roofcsum',round(sum(sum(d.color) for d in r.data.attributes['roofc'].data),3),'schic',{o.instance_collection.name for o in bpy.data.objects if o.name.startswith('SCH_win_')})
PY
for f in $C montclair_state_pre_20261031oh.blend; do echo $f; $B -b $f --python /tmp/oh_count.py 2>&1 | grep COUNT; done
rm -f $C ${C}1
