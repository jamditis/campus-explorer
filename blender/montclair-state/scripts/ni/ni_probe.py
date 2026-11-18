import bpy, mathutils
A,B=-22.930214,0.238365
for o in bpy.data.objects:
    if o.type!='MESH' or o.hide_render: continue
    bb=[o.matrix_world@mathutils.Vector(c) for c in o.bound_box]
    x0=min(v.x for v in bb);x1=max(v.x for v in bb);y0=min(v.y for v in bb);y1=max(v.y for v in bb);z0=min(v.z for v in bb);z1=max(v.z for v in bb)
    if x1>-21.5 and x0<-19.0 and y1>9.4 and y0<14.3 and z1>137.6 and z0<141.5:
        print('OBJ|%s|%d|x %.2f..%.2f y %.2f..%.2f z %.2f..%.2f|%s|%s'%(o.name,len(o.data.vertices),x0,x1,y0,y1,z0,z1,[s.material.name if s.material else None for s in o.material_slots][:3],[c.name for c in o.users_collection]))
