import bpy
nt=bpy.data.materials['cd_grass'].node_tree
for n in nt.nodes: print('N',n.name,n.type)
for l in nt.links: print('L',l.from_node.name,l.from_socket.name,'->',l.to_node.name,l.to_socket.name)
