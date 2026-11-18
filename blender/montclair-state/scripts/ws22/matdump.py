import bpy
mt=bpy.data.materials['Ground_ortho_grass']; nt=mt.node_tree
print('NODES',len(nt.nodes))
for n in nt.nodes:
    extra=''
    if n.bl_idname=='ShaderNodeMapping': extra=str([tuple(round(x,5) for x in n.inputs[k].default_value) for k in ('Location','Rotation','Scale')])
    if n.bl_idname=='ShaderNodeMath' or n.bl_idname=='ShaderNodeMix': extra=getattr(n,'operation',getattr(n,'blend_type',''))
    if n.bl_idname=='ShaderNodeTexImage': extra=n.image.name if n.image else ''
    print('N',n.name,n.bl_idname,extra)
for l in nt.links: print('L',l.from_node.name,'.',l.from_socket.name,'->',l.to_node.name,'.',l.to_socket.identifier)
