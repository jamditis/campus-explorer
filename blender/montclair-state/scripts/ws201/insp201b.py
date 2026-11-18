import bpy
m=bpy.data.materials['fn_lot_asphalt']
for nd in m.node_tree.nodes:
    extra=''
    if nd.type=='TEX_IMAGE': extra=(nd.image.filepath, nd.image.size[:], nd.interpolation, nd.projection)
    if nd.type=='MAPPING': extra=[tuple(round(x,4) for x in nd.inputs[k].default_value) for k in ('Location','Rotation','Scale')]
    if nd.type=='MATH': extra=(nd.operation, [i.default_value for i in nd.inputs if hasattr(i,'default_value')])
    if nd.type=='VALTORGB': extra=[(round(e.position,3),tuple(round(c,3) for c in e.color)) for e in nd.color_ramp.elements]
    if nd.type=='MIX' or nd.type=='MIX_RGB': extra=(getattr(nd,'blend_type',''),)
    print('I201b N',nd.name,nd.type,extra,flush=True)
for l in m.node_tree.links: print('I201b L',l.from_node.name,l.from_socket.name,'->',l.to_node.name,l.to_socket.name,flush=True)
