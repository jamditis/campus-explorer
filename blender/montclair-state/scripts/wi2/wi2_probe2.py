import bpy, json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
O=bpy.data.objects
C=json.load(open('/workspace/nj-scenes/montclair-state/scripts/wi2/cells.json'))
v=C['verge']; l=C['lawn']
import random; random.seed(1)
pts=[('verge',tuple(k)) for k in random.sample(v,6)]+[('lawn',tuple(k)) for k in random.sample(l,8)]
cand=[]
for o in O:
    if o.type!='MESH' or 'grass_points' in o.name or len(o.data.polygons)==0: continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    if min(b.x for b in bb)<160 and max(b.x for b in bb)>130 and min(b.y for b in bb)<310 and max(b.y for b in bb)>280: cand.append(o)
B={}
for o in cand:
    m=o.matrix_world; B[o.name]=BVHTree.FromPolygons([m@x.co for x in o.data.vertices],[tuple(p.vertices) for p in o.data.polygons])
for c,(x,y) in pts:
    x+=0.25;y+=0.25; hits=[]
    for n,b in B.items():
        h=b.ray_cast(Vector((x,y,500)),Vector((0,0,-1)))
        if h[0] is not None:
            o=O[n]; mi=o.data.polygons[h[2]].material_index if o.material_slots else 0
            mat=o.material_slots[mi].material.name if o.material_slots and o.material_slots[mi].material else None
            hits.append((round(h[0].z,3),n[:40],mat))
    hits.sort(reverse=True); print('PT',c,x,y,hits[:3])
