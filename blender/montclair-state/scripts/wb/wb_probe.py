import bpy,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
O=bpy.data.objects; dg=bpy.context.evaluated_depsgraph_get()
def bb(n):
    o=O[n]; V=np.array([o.matrix_world@v.co for v in o.data.vertices]); return V.min(0).round(2),V.max(0).round(2),len(V)
for n in ['QS_footway_313027435_UNVERIFIED','QS_footway_313027429_UNVERIFIED','QS_footway_313027436_UNVERIFIED','QS_footway_313027428_UNVERIFIED','QS_footway_313027432_UNVERIFIED','WT_richardson_west_LiDAR_patch_UNVERIFIED']:
    print(n,bb(n) if n in O else 'MISSING')
for n in O.keys():
    if n.startswith('WF_east_dorm_LiDAR') or n.startswith('WU_richardson_reid'): print(n,bb(n))
def bvh(o):
    e=o.evaluated_get(dg); m=e.to_mesh(); b=BVHTree.FromPolygons([o.matrix_world@v.co for v in m.vertices],[tuple(p.vertices) for p in m.polygons]); e.to_mesh_clear(); return b
GN=[n for n in O.keys() if O[n].type=='MESH' and n.startswith(('WT_richardson_west_LiDAR','RZ2_','WF_east_dorm_LiDAR','WU_richardson_reid','QW_DTM'))]
G={n:bvh(O[n]) for n in GN}
W=bvh(O['QS_footway_313027435_UNVERIFIED'])
# sample walk-435 top along y>305 and lawn beside
for y in np.arange(305,323,1.0):
    row=[]
    for x in np.arange(38,78,0.25):
        h=W.ray_cast(Vector((x,y,500)),Vector((0,0,-1)))
        if h[0] is not None: row.append((x,h[0].z))
    if not row: continue
    xs=[r[0] for r in row]; zt=np.mean([r[1] for r in row])
    out=[]
    for x in (min(xs)-0.5,max(xs)+0.5):
        zz={n[:4]:round(h[0].z,3) for n,b in G.items() for h in [b.ray_cast(Vector((x,y,500)),Vector((0,0,-1)))] if h[0] is not None}
        out.append((round(x,2),zz))
    print('y',y,'walk x',round(min(xs),2),round(max(xs),2),'top',round(zt,3),out)
