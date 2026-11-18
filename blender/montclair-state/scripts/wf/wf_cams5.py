import bpy, math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
import os; os.chdir('/workspace/nj-scenes/montclair-state')
dg=bpy.context.evaluated_depsgraph_get()
P=bpy.data.objects['WF_east_dorm_LiDAR_terrain_patch_UNVERIFIED']
Pe=P.evaluated_get(dg); pme=Pe.to_mesh()
bp=BVHTree.FromPolygons([P.matrix_world@v.co for v in pme.vertices],[tuple(p.vertices) for p in pme.polygons]); Pe.to_mesh_clear()
def gz(x,y):
    h=bp.ray_cast(Vector((x,y,400)),Vector((0,0,-1)))
    return h[0].z if h[0] is not None else None
def setcam(name,loc,look,lens=32):
    o=bpy.data.objects.get(name)
    if o is None:
        c=bpy.data.cameras.new(name); o=bpy.data.objects.new(name,c); bpy.context.scene.collection.objects.link(o)
    o.location=Vector(loc); o.rotation_euler=(Vector(look)-Vector(loc)).to_track_quat('-Z','Y').to_euler()
    o.data.lens=lens; o.data.clip_end=30000; o['wf_obj']=1
    print(name, [round(v,2) for v in loc], 'g_here', gz(loc[0],loc[1]))

# Tree 004 at 246.5,321.5 ground 110.41 — cam south of it on open slope looking N at base
tx,ty=246.5,321.5; tg=gz(tx,ty)
# place cam at (246.5, 312) — south, outside
cx,cy=246.5, 312.0; cg=gz(cx,cy)
print('tree g',tg,'cam site g',cg)
if cg is None: cg=tg-2
setcam('WF_CAM_closeup_tree_bases_east_slope', (cx,cy,cg+1.6), (tx,ty,tg+0.2), 35)

# Patch edge south of Bohn: stand on patch looking at edge
cx,cy=180.0, 325.0; cg=gz(cx,cy); print('edge cam g',cg)
setcam('WF_CAM_closeup_patch_ground_N_stair', (cx,cy,cg+1.8), (200,340,cg+0.3), 32)

# Elevate NW eye higher for clearer view (same XY)
o=bpy.data.objects['WF_CAM_eye_east_dorms_from_NW']
g=gz(o.location.x,o.location.y) or o.location.z-2
o.location.z=g+18  # elevated
o.rotation_euler=(Vector((220,420,140))-o.location).to_track_quat('-Z','Y').to_euler()
print('NW elevated', [round(v,2) for v in o.location])

# SW eye elevate a bit
o=bpy.data.objects['WF_CAM_eye_east_slope_from_SE']
g=gz(o.location.x,o.location.y) or o.location.z-2
o.location.z=g+6
o.rotation_euler=(Vector((210,400,138))-o.location).to_track_quat('-Z','Y').to_euler()
print('SW elevated', [round(v,2) for v in o.location])

bpy.ops.wm.save_mainfile(); print('SAVED',len(bpy.data.objects))
