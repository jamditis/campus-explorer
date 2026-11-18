import bpy
from mathutils import Vector
for o in bpy.data.objects:
    l=o.name.lower()
    if any(k in l for k in ('red hawk','redhawk','hawk','annex','collegeav','normalave','deck')) and o.type in('MESH','CURVE','CAMERA'):
        bb=[o.matrix_world@Vector(c) for c in o.bound_box]
        xs=[v.x for v in bb]; ys=[v.y for v in bb]; zs=[v.z for v in bb]
        mats=[m.name for m in getattr(o.data,'materials',[]) if m][:3] if o.type=='MESH' else []
        print(o.type,'|',o.name,'|',[round(min(xs)),round(max(xs)),round(min(ys)),round(max(ys)),round(min(zs),1),round(max(zs),1)],'|',len(o.data.polygons) if o.type=='MESH' else '', mats, 'hid' if o.hide_render else '')
