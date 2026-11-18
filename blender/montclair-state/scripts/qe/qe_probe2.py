import bpy
m=bpy.data.materials['Wall_stucco_mission']
print('USERS',m.users)
for n in m.node_tree.nodes: print('N',n.name,n.type,n.label)
for l in m.node_tree.links: print('L',l.from_node.name,l.from_socket.name,'->',l.to_node.name,l.to_socket.name)
for on in ['Center for Computing and Information Science walls','Center for Computing and Information Science roof (LiDAR)']:
    o=bpy.data.objects[on]; print('ME',on,o.data.name,o.data.users,[ (s.link,s.material.name) for s in o.material_slots])
