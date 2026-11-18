import bpy
nt=bpy.data.materials['Ground_ortho_grass'].node_tree
out=[n for n in nt.nodes if n.type=='OUTPUT_MATERIAL']; print('OUTS',[(n.name,n.is_active_output,n.target) for n in out])
for n in out:
    for l in n.inputs['Surface'].links: print('SURF',n.name,'<-',l.from_node.name,l.from_node.type)
for l in nt.links:
    if l.to_node.type in ('BSDF_PRINCIPLED','MIX_SHADER','ADD_SHADER','BSDF_DIFFUSE') : print('L',l.from_node.name,'->',l.to_node.name,l.to_socket.name)
print([n.name for n in nt.nodes if n.type=='BSDF_PRINCIPLED'])
