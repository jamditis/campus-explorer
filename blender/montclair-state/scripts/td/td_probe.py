import bpy
from mathutils import Vector
for o in bpy.data.objects:
    n=o.name
    if any(k in n for k in ('Webster','Bohn','Blanton','Stone','Reid','313029100','Lot17','Lot_17','313029107')): print('NAME',n,o.type,o.hide_render,[round(v,1) for v in o.matrix_world.translation])
for o in bpy.data.objects:
    if o.type!='MESH' or o.hide_render: continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]; xs=[v.x for v in bb]; ys=[v.y for v in bb]
    cx=(min(xs)+max(xs))/2; cy=(min(ys)+max(ys))/2
    if 90<cx<200 and 300<cy<460 and (max(xs)-min(xs))<300: print('BOX',o.name,round(min(xs)),round(max(xs)),round(min(ys)),round(max(ys)),round(min(v.z for v in bb),1),round(max(v.z for v in bb),1),len(o.data.polygons))
for c in bpy.data.objects:
    if c.type=='CAMERA' and c.name.startswith('SG_'): print('CAM',c.name,[round(v,1) for v in c.location],[round(v,2) for v in c.rotation_euler])
