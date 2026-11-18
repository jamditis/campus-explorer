import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
dg=bpy.context.evaluated_depsgraph_get(); bv={}
for o in bpy.data.objects:
    if o.type!='MESH': continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    if max(v.x for v in bb)<-218 or min(v.x for v in bb)>-214 or max(v.y for v in bb)<-204 or min(v.y for v in bb)>-200.5: continue
    e=o.evaluated_get(dg); me=e.to_mesh(); mw=o.matrix_world
    if len(me.polygons): bv[o.name]=BVHTree.FromPolygons([tuple(mw@v.co) for v in me.vertices],[tuple(p.vertices) for p in me.polygons])
    e.to_mesh_clear()
for x in (-216.6,-216.2,-215.9,-215.7):
  for y in (-201.4,-201.8,-202.4,-203.0):
    r=[]
    for n,b in bv.items():
        h=b.ray_cast(Vector((x,y,130)),Vector((0,0,-1)),20)
        if h[0] is not None and h[0].z<126: r.append((round(h[0].z,2),n[:34]))
    print('C',x,y,sorted(r,reverse=True)[:3])
