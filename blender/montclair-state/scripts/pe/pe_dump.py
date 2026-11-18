import bpy
m=bpy.data.materials['North_wall_Dickson_brick_buff']
for n in m.node_tree.nodes:
    ins=[(i.name, tuple(round(x,3) for x in i.default_value) if hasattr(i.default_value,'__len__') else round(i.default_value,3) if isinstance(i.default_value,float) else '') for i in n.inputs if not i.is_linked and i.enabled and hasattr(i,'default_value')][:6]
    extra=getattr(n,'operation',getattr(n,'blend_type',getattr(n,'attribute_name','')))
    print('N',n.name,n.type,extra,ins)
for l in m.node_tree.links: print('L',l.from_node.name,l.from_socket.name,'->',l.to_node.name,l.to_socket.identifier)
