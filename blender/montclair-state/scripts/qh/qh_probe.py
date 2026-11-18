import bpy, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
dg=bpy.context.evaluated_depsgraph_get()
T=bpy.data.objects['Terrain_LiDAR_DTM_1m']; Te=T.evaluated_get(dg); em=Te.to_mesh(); MW=T.matrix_world
vs=[MW@v.co for v in em.vertices]; ps=[tuple(p.vertices) for p in em.polygons]; areas=[p.area for p in em.polygons]
bvh=BVHTree.FromPolygons(vs,ps)
xs=[v.x for v in vs]; ys=[v.y for v in vs]; print('TERR ext',min(xs),max(xs),min(ys),max(ys),len(ps))
D=np.load('north/data/grid_1m.npz')['dtm_filled']
def lid(x,y): return float(D[int(y+260),int(x+600)])
print('     y\\x '+' '.join('%6d'%x for x in range(170,221,5)))
for y in range(262,195,-4):
    row=[]
    for x in range(170,221,5):
        xx=min(x,219.5)
        loc,n,fi,d=bvh.ray_cast(Vector((xx,y+0.5,400)),Vector((0,0,-1)))
        row.append('%6s'%('-' if loc is None else '%+.1f%s'%(loc.z-lid(xx,y+0.5),'s' if areas[fi]<0.5 else '')))
    print('%6d '%y+' '.join(row))
# beyond x 220: terrain z
for y in (210,230,250):
    print('east',y,[ (x,round(bvh.ray_cast(Vector((x,y,400)),Vector((0,0,-1)))[0].z,1) if bvh.ray_cast(Vector((x,y,400)),Vector((0,0,-1)))[0] else None) for x in (215,220,225,235,250)])
# other ground objects there
for o in bpy.data.objects:
    if o.type=='MESH' and not o.hide_render:
        bb=[o.matrix_world@Vector(c) for c in o.bound_box]
        if min(v.x for v in bb)<225 and max(v.x for v in bb)>190 and min(v.y for v in bb)<250 and max(v.y for v in bb)>210 and max(o.dimensions)<300:
            print('OBJ',o.name,[round(min(v.z for v in bb),1),round(max(v.z for v in bb),1)])
Te.to_mesh_clear()
