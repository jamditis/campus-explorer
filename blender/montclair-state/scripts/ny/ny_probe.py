import bpy, mathutils
sc=bpy.context.scene; print('RES',sc.render.resolution_x,sc.render.resolution_y,sc.render.resolution_percentage)
for o in bpy.data.objects:
    n=o.name.lower()
    if 'chair' in n and o.type=='MESH':
        cs=[o.matrix_world@mathutils.Vector(c) for c in o.bound_box]
        lo=[round(min(c[i] for c in cs),2) for i in range(3)]; hi=[round(max(c[i] for c in cs),2) for i in range(3)]
        if -25<lo[0]<20 and -20<lo[1]<30:
            print('CH',o.name,'|',o.users_collection[0].name,len(o.data.vertices),len(o.data.polygons),lo,hi,[s.material.name if s.material else None for s in o.material_slots], o.parent.name if o.parent else None)
