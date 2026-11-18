import bpy
m=bpy.data.materials['Roof_tile_or_membrane']; nt=m.node_tree
for n in nt.nodes:
    extra=''
    if n.type=='MATH' or n.type=='VECT_MATH': extra=n.operation+' '+str([round(i.default_value,3) if hasattr(i,'default_value') and isinstance(i.default_value,float) else '' for i in n.inputs])
    if n.type=='ATTRIBUTE': extra=n.attribute_name
    if n.type=='VALTORGB': extra=str([round(e.position,3) for e in n.color_ramp.elements])
    if n.type=='MAP_RANGE': extra=str([round(i.default_value,3) for i in n.inputs if hasattr(i,'default_value') and isinstance(i.default_value,float)])
    print('N',n.name,n.type,n.label,extra)
for l in nt.links: print('L',l.from_node.name,l.from_socket.name,'->',l.to_node.name,l.to_socket.name)
