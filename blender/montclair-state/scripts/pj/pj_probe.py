import bpy
from mathutils import Vector
c=bpy.data.objects['PF_CAM_eye_feliciano_east']; print('CAM',tuple(round(v,2) for v in c.location), tuple(round(v,2) for v in c.rotation_euler))
for o in bpy.data.objects:
    if o.type!='MESH': continue
    bb=[o.matrix_world@Vector(b) for b in o.bound_box]
    x0=min(v.x for v in bb);x1=max(v.x for v in bb);y0=min(v.y for v in bb);y1=max(v.y for v in bb)
    if x1<-275 or x0>-186 or y1<134 or y0>250: continue
    if (x1-x0)>300: continue
    print(o.name,'|',o.users_collection[0].name,'|',len(o.data.polygons),'| x',round(x0,1),round(x1,1),'y',round(y0,1),round(y1,1),'z',round(min(v.z for v in bb),1),round(max(v.z for v in bb),1),'|',[s.material.name if s.material else None for s in o.material_slots][:4], 'hide',o.hide_render)
