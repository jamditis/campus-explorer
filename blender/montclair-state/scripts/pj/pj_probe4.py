import bpy
m=bpy.data.materials['OM_Schmitt_sill_drip_grime_UNVERIFIED']
print('BM',m.blend_method)
for n in m.node_tree.nodes:
    print('N',n.bl_idname,n.name,[ (i.name, round(i.default_value,3) if isinstance(i.default_value,float) else '') for i in n.inputs if not i.is_linked and hasattr(i,'default_value')][:6])
for l in m.node_tree.links: print('L',l.from_node.name,l.from_socket.name,'->',l.to_node.name,l.to_socket.name)
