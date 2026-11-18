import bpy
for n in ['TN_precast_pier_UNVERIFIED','TN_spandrel_band_UNVERIFIED','TN_block_base_UNVERIFIED','TR_Blanton_infill_cream_UNVERIFIED']:
    m=bpy.data.materials[n]; nt=m.node_tree
    print('==',n)
    for nd in nt.nodes:
        extra=''
        if nd.type=='VALTORGB': extra=[(round(e.position,2),tuple(round(c,3) for c in e.color)) for e in nd.color_ramp.elements]
        if nd.type in('RGB',): extra=tuple(round(c,3) for c in nd.outputs[0].default_value)
        if nd.type=='MIX': extra=(nd.data_type,nd.blend_type, [tuple(round(x,3) for x in i.default_value) if hasattr(i.default_value,'__len__') else round(i.default_value,3) for i in nd.inputs if not i.is_linked and i.enabled][:4])
        print(' ',nd.name,nd.type,extra)
    for l in nt.links: print('  L',l.from_node.name,l.from_socket.name,'->',l.to_node.name,l.to_socket.name)
