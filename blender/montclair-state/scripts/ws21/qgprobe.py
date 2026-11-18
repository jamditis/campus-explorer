import bpy
ng=bpy.data.node_groups['QG_north_strip_LiDAR_patch_GN']
print('USERS',ng.users)
for n in ng.nodes:
    print('N',n.name,n.type,getattr(n,'domain',''),getattr(n,'mode',''),[(i.name,i.default_value if hasattr(i,'default_value') and not i.is_linked and i.type in('VALUE','VECTOR','BOOLEAN','INT') else '') for i in n.inputs], n.inputs[0].default_value.name if n.type=='OBJECT_INFO' and n.inputs[0].default_value else '')
for l in ng.links: print('L',l.from_node.name,l.from_socket.name,'->',l.to_node.name,l.to_socket.name)
for m in bpy.data.objects['Terrain_LiDAR_DTM_1m'].modifiers:
    if m.name.startswith('QG'): print('MODKEYS',dict(m.items()) if hasattr(m,'items') else '')
