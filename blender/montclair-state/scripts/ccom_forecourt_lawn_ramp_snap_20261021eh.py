# Session eh: after the eh lawn ramp, ~100 raised grass points float 2-13 cm above the 1 m DTM (the DTM interpolates between
# raised/unraised verts). Snap eh-raised grass points that sit > 1 cm above the terrain down onto it. Revert = REVERT=1 on
# ccom_forecourt_lawn_ramp_20261021eh.py (eh_orig_z holds the pre-ramp z). SAVE=1 saves.
import bpy, bmesh, mathutils, re, os
from mathutils.bvhtree import BVHTree
ter=bpy.data.objects['Terrain_LiDAR_DTM_1m']; tb=bmesh.new(); tb.from_mesh(ter.data); tb.transform(ter.matrix_world); tv=BVHTree.FromBMesh(tb)
for o in bpy.data.objects:
    if o.type!='MESH' or not re.match(r'(?i)^(dS_grass|cx_grass|cd_grass|Lawn_grass_instanced)',o.name): continue
    at=o.data.attributes.get('eh_orig_z')
    if not at: continue
    oi=o.matrix_world.inverted(); n=0
    for v,d in zip(o.data.vertices,at.data):
        if d.value<-9000: continue
        w=o.matrix_world@v.co; h=tv.ray_cast(mathutils.Vector((w.x,w.y,w.z+5)),mathutils.Vector((0,0,-1)))
        if h[0] and 0.01<w.z-h[0].z<0.3:
            v.co.z=(oi@mathutils.Vector((w.x,w.y,max(h[0].z,d.value)))).z; n+=1
    o.data.update(); print('EH_SNAP',o.name,n)
if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('EH_SAVED')
