import bpy, mathutils
for o in bpy.data.objects:
    if o.type!='MESH': continue
    bb=[o.matrix_world@mathutils.Vector(c) for c in o.bound_box]
    x0=min(v.x for v in bb);x1=max(v.x for v in bb);y0=min(v.y for v in bb);y1=max(v.y for v in bb);z0=min(v.z for v in bb);z1=max(v.z for v in bb)
    if x1>-10 and x0<-3 and y1>6 and y0<17 and z1>141.5 and z0<144.5 and (x1-x0)<30:
        print('S|%s|hr=%s|%d|x %.2f..%.2f y %.2f..%.2f z %.2f..%.2f|%s'%(o.name,o.hide_render,len(o.data.vertices),x0,x1,y0,y1,z0,z1,[s.material.name if s.material else None for s in o.material_slots][:3]))
