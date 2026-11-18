import bpy
for cn in ['TN_Blanton_precast_frame_UNVERIFIED']:
    c=bpy.data.collections.get(cn)
    print(cn, c and [(o.name,o.type,len(o.data.polygons) if o.type=='MESH' else 0) for o in c.all_objects][:20])
for o in bpy.data.objects:
    if o.name.startswith('TJ_Blanton_entrance') or ('Blanton' in o.name and o.name.startswith(('TJ','TN','TR'))):
        import mathutils
        bb=[o.matrix_world@mathutils.Vector(v) for v in o.bound_box]
        xs=[v.x for v in bb]; ys=[v.y for v in bb]; zs=[v.z for v in bb]
        print(o.name,o.type,[c.name for c in o.users_collection],'x %.1f..%.1f y %.1f..%.1f z %.1f..%.1f'%(min(xs),max(xs),min(ys),max(ys),min(zs),max(zs)), o.hide_render, len(o.modifiers))
