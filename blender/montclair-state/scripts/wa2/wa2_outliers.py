"""wa2: list QT outer verts >15 cm above ground and the first mesh hit from above (scene ray)."""
import bpy, numpy as np, json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
O=bpy.data.objects; dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
def bvh(o):
    e=o.evaluated_get(dg); m=e.to_mesh(); b=BVHTree.FromPolygons([o.matrix_world@v.co for v in m.vertices],[tuple(p.vertices) for p in m.polygons]); e.to_mesh_clear(); return b
G=[(n,bvh(O[n])) for n in O.keys() if O[n].type=='MESH' and n.startswith(('WV_stone','WN_south','WO_gully','Terrain_LiDAR','QW_DTM','WU_rich','WT_rich','WF_east','RZ2_','WA0_'))]
def gz(x,y):
    z=[(h[0].z,n) for n,b in G for h in [b.ray_cast(Vector((x,y,500)),Vector((0,0,-1)))] if h[0] is not None]
    return max(z) if z else (None,None)
out=[]
for t in [o for o in O if o.name.startswith('QT_soil_edge_') and '546643369' not in o.name]:
    S=bvh(O[t.name.replace('QT_soil_edge_','QS_footway_')]); mw=t.matrix_world
    for p in t.data.polygons:
        ws=[mw@t.data.vertices[i].co for i in p.vertices]; d=[S.find_nearest(v)[3] for v in ws]
        for k in np.argsort(d)[2:]:
            v=ws[k]; g,gn=gz(v.x,v.y)
            if g is None or v.z-g<0.15: continue
            r=sc.ray_cast(dg,Vector((v.x,v.y,v.z+30)),Vector((0,0,-1)))
            out.append((t.name[13:22],round(v.x,1),round(v.y,1),round((v.z-g)*100),gn,r[4].name if r[0] else None, round(r[1].z-v.z,2) if r[0] else None))
seen=set()
for o in out:
    key=(o[0],round(o[1]),round(o[2]))
    if key in seen: continue
    seen.add(key); print('OUT',o)
print('N',len(out))
