import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
dg=bpy.context.evaluated_depsgraph_get()
def bvh(o,ev=True):
    me=(o.evaluated_get(dg).to_mesh() if ev else o.data); mw=o.matrix_world
    return BVHTree.FromPolygons([mw@v.co for v in me.vertices],[p.vertices[:] for p in me.polygons])
ter=bpy.data.objects['Terrain_LiDAR_DTM_1m']; sk=bpy.data.objects['Context_skirt_3DEP_ortho_4km']
bt=bvh(ter); bs=bvh(sk,False)
def z(b,x,y):
    h=b.ray_cast(Vector((x,y,500)),Vector((0,0,-1))); return round(h[0].z,1) if h[0] else None
for x in (-90,-60,0,40,70,120):
    print('PROF x',x,[(y,z(bt,x,y),z(bs,x,y)) for y in range(196,262,6)])
tr=[o for o in bpy.data.objects if o.name.startswith('T_') and 225<o.location.y<250]
print('TREES strip',len(tr),[(o.name,round(o.location.x),round(o.location.y),round(o.location.z,1),z(bt,o.location.x,o.location.y),z(bs,o.location.x,o.location.y)) for o in tr[:15]])
