import bpy
from mathutils import Vector
X0,X1,Y0,Y1=-340,-150,-350,-160
keep=('Terrain_LiDAR','Context_skirt','WS68_RHD_ground','WP2_Sun','Sun')
rm=[]
for o in bpy.data.objects:
    if o.type in ('CAMERA','LIGHT') or o.name.startswith(keep): continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]; xs=[v.x for v in bb]; ys=[v.y for v in bb]
    if max(xs)<X0 or min(xs)>X1 or max(ys)<Y0 or min(ys)>Y1: rm.append(o)
print('CUT removing',len(rm),'of',len(bpy.data.objects))
bpy.data.batch_remove(rm)
bpy.data.orphans_purge(do_local_ids=True,do_linked_ids=True,do_recursive=True)
bpy.ops.wm.save_as_mainfile(filepath='/workspace/nj-scenes/montclair-state/scripts/ws112/render_cut112.blend',copy=True)
print('CUT SAVED')
