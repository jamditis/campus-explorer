import bpy
m=bpy.data.materials['Roof_tile_or_membrane']
print('USERS',m.users,[o.name for o in bpy.data.objects if o.type=='MESH' and any(s.material==m for s in o.material_slots)][:40])
for n in m.node_tree.nodes:
    print('N',n.name,n.type,n.label,[ (i.name, i.default_value if hasattr(i,'default_value') and not i.is_linked and i.type in('VALUE',) else '') for i in n.inputs][:6], getattr(n,'operation',''), getattr(n,'attribute_name',''))
for l in m.node_tree.links: print('L',l.from_node.name,l.from_socket.name,'->',l.to_node.name,l.to_socket.name)
o=bpy.data.objects['Susan A. Cole Hall roof (LiDAR)']
print('ROOF',len(o.data.polygons),[s.material.name for s in o.material_slots],[m.type for m in o.modifiers], o.data.attributes.keys())
