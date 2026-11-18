import bpy, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
dg=bpy.context.evaluated_depsgraph_get()
T=bpy.data.objects['Terrain_LiDAR_DTM_1m']; bt=BVHTree.FromObject(T,dg); bs=BVHTree.FromObject(bpy.data.objects['Context_skirt_3DEP_ortho_4km'],dg)
D=np.load('north/data/grid_1m.npz')['dtm_filled']
def r(b,x,y):
    h=b.ray_cast(Vector((x,y,400)),Vector((0,0,-1)))[0]; return None if h is None else round(h.z,1)
for x in (155,170,185,200,215):
    print('N',x,[(y,r(bt,x,y),r(bs,x,y),round(float(D[int(y)+260,x+600]),1)) for y in (244.5,248.5,249.5,252,256)])
for y in (0,100,180):
    print('E',y,[(x,r(bt,x,y),r(bs,x,y)) for x in (225,235,240,245,247,250)])
# what renders north of y 250 at x 170?
hits=[]
for o in bpy.data.objects:
    if o.type!='MESH' or o.hide_render: continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    if min(v.x for v in bb)<170<max(v.x for v in bb) and min(v.y for v in bb)<256<max(v.y for v in bb) and max(v.x for v in bb)-min(v.x for v in bb)<3000: hits.append(o.name)
print('OBJS at (170,256)',hits[:20])
