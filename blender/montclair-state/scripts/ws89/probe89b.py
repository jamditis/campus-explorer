import bpy,math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
with bpy.data.libraries.load('/workspace/nj-scenes/montclair-state/montclair_state.blend') as (s,d):
    d.objects=['COLE_plaza_deck_bs','COLE_plaza_edge_bs']
C=Vector((-166.66,-79.9))
for o in d.objects:
    P=[o.matrix_world@v.co for v in o.data.vertices]
    bvh=BVHTree.FromPolygons(P,[tuple(p.vertices) for p in o.data.polygons])
    for ang in range(150,256,10):
        a=math.radians(ang); row=[]
        for r in [8,12,14,16,17.8,18.5,19.5,20.5,21.5,23,25,28,31,34]:
            q=C+Vector((math.cos(a),math.sin(a)))*r
            h=bvh.ray_cast(Vector((q.x,q.y,140)),Vector((0,0,-1)))
            row.append(f"{r}:{h[0].z:.2f}" if h[0] else f"{r}:--")
        print('P89B',o.name[:14],ang,' '.join(row))
