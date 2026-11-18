import bpy
from mathutils import Vector
for o in bpy.data.objects:
    if o.type!='MESH' or o.hide_render: continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    mn=[min(v[i] for v in bb) for i in range(3)]; mx=[max(v[i] for v in bb) for i in range(3)]
    if mx[0]>-26 and mn[0]<-14 and mx[1]>2 and mn[1]<17 and mx[2]>143 and mn[2]<150 and (mx[0]-mn[0])<60:
        print('O',o.name,[round(x,2) for x in mn],[round(x,2) for x in mx],len(o.data.polygons),[m.name for m in o.data.materials if m][:4])
