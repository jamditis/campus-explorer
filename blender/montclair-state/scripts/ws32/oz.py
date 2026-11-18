import bpy
m=bpy.data.materials['OZ_walk_joint_grid_auto_UNVERIFIED']
for n in m.node_tree.nodes:
    ins={i.name:(tuple(round(x,3) for x in i.default_value) if hasattr(i.default_value,'__len__') else round(i.default_value,3)) for i in n.inputs if hasattr(i,'default_value') and not i.is_linked}
    print('N',n.type,n.name,getattr(n,'attribute_name',''),getattr(n,'blend_method',''),{k:v for k,v in list(ins.items())[:8]})
for l in m.node_tree.links: print('L',l.from_node.name,l.from_socket.name,'->',l.to_node.name,l.to_socket.name)
md=bpy.data.objects['OZ_walk_joints_auto_GN_UNVERIFIED'].modifiers[0]
print('MOD',[(k,md[k]) for k in md.keys()][:20])
