import bpy
m=bpy.data.materials['PI_Feliciano_roof_tile_forced_UNVERIFIED']
for l in m.node_tree.links:
    if l.to_node.type in('MAPPING','TEX_IMAGE') or l.from_node.type=='TEX_COORD': print('L',l.from_node.name,l.from_socket.name,'->',l.to_node.name,l.to_socket.name)
mp=m.node_tree.nodes['Mapping']; print('MAP',[tuple(round(x,3) for x in i.default_value) for i in mp.inputs[1:]])
o=bpy.data.objects['PN_Feliciano_hip_roof_0_UNVERIFIED']; print('UV',[u.name for u in o.data.uv_layers],[a.name+':'+a.domain for a in o.data.attributes])
