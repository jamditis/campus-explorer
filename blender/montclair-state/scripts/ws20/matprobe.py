import bpy
o=bpy.data.objects['Life Hall walls']
print('UVS',[u.name for u in o.data.uv_layers], 'attrs',[a.name for a in o.data.attributes])
m=o.data.materials[0]
for n in m.node_tree.nodes:
    extra=''
    if n.type=='TEX_IMAGE' and n.image: extra=n.image.filepath
    if n.type=='UVMAP': extra=n.uv_map
    if n.type=='ATTRIBUTE': extra=n.attribute_name
    print('N',n.type,n.name,extra,[ (l.from_node.name,l.to_socket.name) for i in n.inputs for l in i.links])
