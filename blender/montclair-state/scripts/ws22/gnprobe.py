import bpy
ng=bpy.data.node_groups['QG_north_strip_LiDAR_patch_GN']
for n in ng.nodes:
    print('N',n.name,n.bl_idname,'mute' if n.mute else '', {i.name:(getattr(i,'default_value',None) if not i.is_linked else 'L') for i in n.inputs if i.enabled and hasattr(i,'default_value') and not hasattr(i.default_value,'__len__')})
    if n.bl_idname=='GeometryNodeObjectInfo': print('  obj',n.inputs['Object'].default_value)
for l in ng.links: print('L',l.from_node.name,l.from_socket.name,'->',l.to_node.name,l.to_socket.name)
o=bpy.data.objects['Terrain_LiDAR_DTM_1m']
for m in o.modifiers: print('MOD',m.name,m.type,getattr(m,'node_group',None) and m.node_group.name, m.show_render)
