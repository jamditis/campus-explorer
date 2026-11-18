import bpy, mathutils
for o in bpy.data.objects:
    n=o.name.lower()
    if o.type=='MESH' and not o.hide_render and ('red' in n and ('wall' in n or 'panel' in n)) or o.name.startswith('NO atrium red-wall washer 0'):
        cs=[o.matrix_world@mathutils.Vector(c) for c in o.bound_box]
        print('Q|',o.name,[round(min(c[i] for c in cs),2) for i in range(3)],[round(max(c[i] for c in cs),2) for i in range(3)])
