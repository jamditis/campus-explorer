import bpy
g=bpy.data.node_groups['WS72_KasserSW_walk_cut']
for l in g.links: print('P223 link %s.%s -> %s.%s'%(l.from_node.name,l.from_socket.identifier,l.to_node.name,l.to_socket.identifier))
for n in g.nodes:
    for s in n.inputs:
        if not s.is_linked and hasattr(s,'default_value'):
            try: print('P223 in',n.name,s.identifier,tuple(s.default_value) if hasattr(s.default_value,'__len__') else s.default_value)
            except Exception: pass
    if n.bl_idname=='GeometryNodeObjectInfo': print('P223 obj', n.inputs[0].default_value.name if n.inputs[0].default_value else None, n.transform_space)
