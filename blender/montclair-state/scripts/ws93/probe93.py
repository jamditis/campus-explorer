import bpy
from mathutils import Vector
X0,X1,Y0,Y1=-224,-204,-96,-78
for o in bpy.data.objects:
    if o.type!='MESH' or o.hide_render: continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    if max(b.x for b in bb)<X0 or min(b.x for b in bb)>X1 or max(b.y for b in bb)<Y0 or min(b.y for b in bb)>Y1: continue
    mw=o.matrix_world; n=sum(1 for v in o.data.vertices if X0<(mw@v.co).x<X1 and Y0<(mw@v.co).y<Y1)
    if n: print('PB',o.name,len(o.data.vertices),n,[m.name for m in o.modifiers][:3],[s.material.name if s.material else None for s in o.material_slots][:3])
