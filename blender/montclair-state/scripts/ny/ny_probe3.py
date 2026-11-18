import bpy, mathutils
for o in bpy.data.objects:
    if (o.name.startswith('dc_side_chair') and o.name.endswith(('_seat','_back'))) or o.name.startswith('CCOM_lounge_chair_0'):
        cs=[o.matrix_world@mathutils.Vector(c) for c in o.bound_box]
        print('P3',o.name,o.hide_render,[round(min(c[i] for c in cs),2) for i in range(3)],[round(max(c[i] for c in cs),2) for i in range(3)],[c.name for c in o.users_collection], [ (c.name) for c in bpy.context.view_layer.layer_collection.children if c.exclude][:3])
