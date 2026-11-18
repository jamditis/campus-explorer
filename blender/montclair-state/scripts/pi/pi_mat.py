import bpy
m=bpy.data.materials['Roof_tile_or_membrane']
for n in m.node_tree.nodes:
    ins={i.name:(round(i.default_value,3) if isinstance(i.default_value,float) else None) for i in n.inputs if hasattr(i,'default_value') and not i.is_linked}
    print('N',n.name,n.bl_idname,getattr(n,'operation',''),getattr(n,'attribute_name',''),{k:v for k,v in ins.items() if v is not None})
for l in m.node_tree.links: print('L',l.from_node.name,l.from_socket.name,'->',l.to_node.name,l.to_socket.name)
r=bpy.data.objects['Feliciano School of Business roof (LiDAR)']
for md in r.modifiers: print('MOD',md.name,md.node_group.name if md.node_group else None)
