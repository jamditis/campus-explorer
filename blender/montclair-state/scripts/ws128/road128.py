import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
P='/workspace/nj-scenes/montclair-state/scripts/ws128/cut128.blend'
with bpy.data.libraries.load(P) as (df,dt):
    dt.objects=[n for n in df.objects if any(k in n for k in ('oad','CollegeAve','sphalt','WS128','WS9','WS10'))]
for o in dt.objects:
    if o is None or o.type!='MESH': continue
    mw=o.matrix_world; t=BVHTree.FromPolygons([mw@v.co for v in o.data.vertices],[p.vertices for p in o.data.polygons])
    for xy in ((-244.5,-240),(-243,-232),(-239.8,-239.5),(-228,-244)):
        r=t.ray_cast(Vector((xy[0],xy[1],200)),Vector((0,0,-1)))
        if r[0] is not None and r[0].z<150:
            p=o.data.polygons[r[2]]; m=o.data.materials[p.material_index] if o.data.materials else None
            print('HIT',xy,o.name,round(r[0].z,3),m.name if m else None)
