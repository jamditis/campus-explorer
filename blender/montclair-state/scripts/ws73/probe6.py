import bpy
m=bpy.data.materials['WS68_Ground_ortho_grass_north2020']
for n in m.node_tree.nodes:
    print('P6 node',n.type,n.name,getattr(n,'image',None) and (n.image.name,n.image.filepath,tuple(n.image.size)))
print('P6 links',[(l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name) for l in m.node_tree.links])
o=[o for o in bpy.data.objects if o.name.startswith('WS68_RHD_ground')][0]
me=o.data; uv=me.uv_layers.active
import random
for i in random.sample(range(len(me.loops)),6):
    l=me.loops[i]; c=o.matrix_world@me.vertices[l.vertex_index].co; print('P6 uv',[round(c.x,1),round(c.y,1)],tuple(round(v,4) for v in uv.data[i].uv))
