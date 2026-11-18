# ws134h: retire the old UA_footway_312845863_south faces that lie under/through the WS133 E walk and the WS134g NE leg
# (dark wavy band poking through both walks at eye level).
import bpy, bmesh, os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
SAVE=os.environ.get('SAVE','0')=='1'
dg=bpy.context.evaluated_depsgraph_get()
def tree(o):
    bm=bmesh.new(); bm.from_mesh(o.data); bm.transform(o.matrix_world); T=BVHTree.FromBMesh(bm); bm.free(); return T
TS=[tree(bpy.data.objects[n]) for n in ('WS133_Russ_E_walk_concrete_LiDAR2023int_UNVERIFIEDjoints',[o.name for o in bpy.data.objects if o.name.startswith('WS134g_')][0])]
u=bpy.data.objects['UA_footway_312845863_south_UNVERIFIED']; mw=u.matrix_world
bm=bmesh.new(); bm.from_mesh(u.data); dl=[]
for f in bm.faces:
    c=mw@f.calc_center_median()
    if c.y<-275 or c.y>-205: continue
    if any(T.ray_cast(Vector((c.x,c.y,c.z+5)),Vector((0,0,-1)),12)[0] is not None for T in TS) or (c.y>-268 and -132<c.x<-105): dl.append(f)
bmesh.ops.delete(bm,geom=dl,context='FACES_ONLY'); bm.to_mesh(u.data); bm.free(); print('UA retired',len(dl))
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
