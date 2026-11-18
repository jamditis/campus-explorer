import bpy, json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
O=bpy.data.objects
C=json.load(open('/workspace/nj-scenes/montclair-state/scripts/wi2/cells.json'))
print('KEYS',list(C.keys()), len(C['verge']))
v=C['verge']
xs=[a for a,b in v]; ys=[b for a,b in v]; print('VBOX',min(xs),max(xs),min(ys),max(ys))
cand=[]
for o in O:
    if o.type!='MESH' or 'grass_points' in o.name or len(o.data.polygons)==0: continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    if min(b.x for b in bb)<147 and max(b.x for b in bb)>121 and min(b.y for b in bb)<298 and max(b.y for b in bb)>247: cand.append(o)
B={}
for o in cand:
    m=o.matrix_world; B[o.name]=BVHTree.FromPolygons([m@x.co for x in o.data.vertices],[tuple(p.vertices) for p in o.data.polygons])
import random; random.seed(2)
mats={}
for (x,y) in random.sample(v,40):
    x+=0.25;y+=0.25; hits=[]
    for n,b in B.items():
        h=b.ray_cast(Vector((x,y,500)),Vector((0,0,-1)))
        if h[0] is not None:
            o=O[n]; mi=o.data.polygons[h[2]].material_index if o.material_slots else 0
            mat=o.material_slots[mi].material.name if o.material_slots and o.material_slots[mi].material else None
            hits.append((round(h[0].z,3),n,mat))
    hits.sort(reverse=True); t=hits[0] if hits else None
    if t: mats[(t[1],t[2])]=mats.get((t[1],t[2]),0)+1
print('TOP',mats)
for (on,mn),c in mats.items():
    m=bpy.data.materials.get(mn)
    if m and m.use_nodes:
        print('MAT',mn,'users',m.users,[ (n.type,n.name) for n in m.node_tree.nodes])
print('QY',[o.name for o in O if o.name.startswith(('QY','QZ','RA'))][:30])
