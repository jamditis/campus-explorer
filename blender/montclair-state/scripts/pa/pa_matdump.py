import bpy
m=bpy.data.materials['Ground_ortho_grass']
for l in m.node_tree.links: print('MD',l.from_node.name,l.from_socket.name,'->',l.to_node.name,l.to_socket.name)
for n in m.node_tree.nodes:
    if n.type=='ATTRIBUTE' or n.type=='VERTEX_COLOR': print('MD attr',n.name,getattr(n,'attribute_name',''))
    if n.type=='TEX_COORD': print('MD tc obj',n.object)
