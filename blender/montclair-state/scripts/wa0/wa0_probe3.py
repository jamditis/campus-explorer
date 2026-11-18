import bpy, json
from collections import defaultdict
from mathutils import Vector
from mathutils.bvhtree import BVHTree
O=bpy.data.objects; dg=bpy.context.evaluated_depsgraph_get()
def bvh(o):
    e=o.evaluated_get(dg); m=e.to_mesh(); b=BVHTree.FromPolygons([o.matrix_world@v.co for v in m.vertices],[tuple(p.vertices) for p in m.polygons]); e.to_mesh_clear(); return b
QW=O['QW_DTM_north_edge_ramp_UNVERIFIED']; WV=O['WV_stone_west_LiDAR_patch_UNVERIFIED']; WU=O['WU_richardson_reid_LiDAR_patch_UNVERIFIED']
print('QW mods',[m.type for m in QW.modifiers],'faces',len(QW.data.polygons),'mat',[m.name for m in QW.data.materials])
print('WV mods',[m.type for m in WV.modifiers])
B={'WV':bvh(WV),'WU':bvh(WU),'QW':bvh(QW)}
def hz(k,x,y):
    h=B[k].ray_cast(Vector((x,y,500)),Vector((0,0,-1))); return None if h[0] is None else round(h[0].z,4)
mw=QW.matrix_world
vs=[mw@v.co for v in QW.data.vertices]
xs=[v.x for v in vs]; ys=[v.y for v in vs]
print('QW bbox x',min(xs),max(xs),'y',min(ys),max(ys))
# open edges of QW with x>110
ec=defaultdict(int)
for p in QW.data.polygons:
    L=list(p.vertices)
    for a,b in zip(L,L[1:]+L[:1]): ec[(min(a,b),max(a,b))]+=1
oe=[(a,b) for (a,b),c in ec.items() if c==1]
rows=[]
for a,b in oe:
    m=(vs[a]+vs[b])/2
    if m.x<110: continue
    zw=hz('WV',m.x,m.y) or hz('WU',m.x,m.y)
    rows.append((round(m.x,2),round(m.y,2),round(m.z,4),zw,None if zw is None else round((m.z-zw)*100,1)))
rows.sort()
print('QW open edges x>110 n',len(rows))
for r in rows[::max(1,len(rows)//60)]: print(' OE',r)
# grid of QW-WV diff
print('grid')
for y in [274+0.25*i for i in range(16)]:
    print(round(y,2),[ (lambda q,w: None if q is None or w is None else round((q-w)*100,1))(hz('QW',x,y),hz('WV',x,y)) for x in range(120,130)])
