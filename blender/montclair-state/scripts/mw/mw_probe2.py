import bpy
from mathutils import Vector
dg=bpy.context.evaluated_depsgraph_get()
for o in bpy.data.objects:
    if o.type not in ('MESH','FONT','CURVE','EMPTY'): continue
    if o.hide_render: continue
    if o.type=='EMPTY' and o.instance_collection is None: continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    mn=[min(v[i] for v in bb) for i in range(3)]; mx=[max(v[i] for v in bb) for i in range(3)]
    if mx[0]>-30 and mn[0]<-16 and mn[1]<8.3 and mx[1]>-28 and mx[2]>137.5 and mn[2]<147:
        sz=[mx[i]-mn[i] for i in range(3)]
        if max(sz)>40: continue
        mats=[s.material.name for s in o.material_slots if s.material][:3] if o.type=='MESH' else []
        print("O2|%s|%s|%s|%s|%s|%s"%(o.name,o.type,[c.name for c in o.users_collection],[round(x,2) for x in mn],[round(x,2) for x in mx],mats))
# wall verts west face
w=bpy.data.objects['School of Communication and Media walls']
M=w.matrix_world
import collections
for p in w.data.polygons:
    c=M@p.center
    if c.x<-18 and c.y<9 and c.y>-28:
        n=(M.to_3x3()@p.normal).normalized()
        if n.x<-0.5:
            vs=[tuple(round(x,2) for x in M@w.data.vertices[i].co) for i in p.vertices]
            print("WF|",p.index,[round(x,3) for x in n],w.data.materials[p.material_index].name if w.data.materials else '',vs)
