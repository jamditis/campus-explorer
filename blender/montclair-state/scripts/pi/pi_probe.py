import bpy
from mathutils import Vector
B=(-226,-202,160,190,160.5,190)
for o in bpy.data.objects:
    if o.type!='MESH' or o.hide_render: continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    x0,x1=min(v.x for v in bb),max(v.x for v in bb); y0,y1=min(v.y for v in bb),max(v.y for v in bb); z0,z1=min(v.z for v in bb),max(v.z for v in bb)
    if x1<B[0] or x0>B[1] or y1<B[2] or y0>B[3] or z1<B[4] or z0>B[5]: continue
    mw=o.matrix_world; n=0; mats=set()
    for p in o.data.polygons:
        c=mw@p.center
        if B[0]<c.x<B[1] and B[2]<c.y<B[3] and B[4]<c.z<B[5]:
            n+=1; mats.add(o.material_slots[p.material_index].material.name if o.material_slots and o.material_slots[p.material_index].material else None)
    if n: print('OBJ',repr(o.name),n,[round(x,1) for x in (x0,x1,y0,y1,z0,z1)],sorted(map(str,mats))[:6])
c=bpy.data.objects['PF_CAM_closeup_feliciano_entrance']; print('CAM',tuple(round(x,1) for x in c.location),tuple(round(x,2) for x in c.rotation_euler))
