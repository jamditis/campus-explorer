# ws62 v2: smooth-shade the clustered crowns (kill low-poly facets), finer leaf-clump bump, fewer grey bare crowns (one grey ramp stop -> dark oak brown). Idempotent.
import bpy, os
for mn in ('WS62_crown_lumpy','WS62_crown_broad','WS62_crown_tall'):
    me=bpy.data.meshes[mn]
    for p in me.polygons: p.use_smooth=True
nt=bpy.data.materials['MID_canopy_carpet_leaf_ai'].node_tree; N=nt.nodes
N['EO_noise'].inputs['Scale'].default_value=5.5
N['EO_bump'].inputs['Strength'].default_value=1.0
r=N['ah_ramp'].color_ramp
for e in r.elements:
    if abs(e.position-0.84)<0.01: e.color=(0.078,0.046,0.022,1)
print('V62 ok')
if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('V62 saved')
