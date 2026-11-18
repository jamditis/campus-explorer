import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
P='/workspace/nj-scenes/montclair-state/montclair_state.blend'
with bpy.data.libraries.load(P) as (df,dt):
    dt.objects=[n for n in df.objects if n.startswith(('WS107_Chapin','WS130_','WS108_Chapin_eave'))]
T=[]
for o in dt.objects:
    if o is None or o.type!='MESH': continue
    T.append((o.name,BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[p.vertices for p in o.data.polygons])))
for y in (-212,-216,-220,-224,-227,-229):
    hits=[]
    for n,t in T:
        if n.startswith('WS130_'): continue
        for z in (122.5,124.0):
            h=t.ray_cast(Vector((-180,y,z)),Vector((-1,0,0)))
            if h[0] is not None: hits.append((round(h[0].x,2),z,n[:40]))
    print('Y',y,sorted(hits,reverse=True)[:3])
