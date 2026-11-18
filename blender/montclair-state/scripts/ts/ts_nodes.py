import bpy
for mn in ('OW2_Context_skirt_ortho_strip_tone_UNVERIFIED','BD_farfield_ortho_haze_bm','BD_farfield_ortho_haze'):
    m=bpy.data.materials.get(mn); print('MAT',mn,m and m.library)
    if not m: continue
    for n in m.node_tree.nodes:
        ex=''
        if n.type=='TEX_IMAGE' and n.image: ex=n.image.filepath+' '+str(tuple(n.image.size))
        if n.type=='MIX': ex=n.blend_type+' '+n.data_type
        if n.type=='VALTORGB': ex=str([tuple(round(c,2) for c in e.color) +(round(e.position,2),) for e in n.color_ramp.elements])
        ins=[(i.name,round(i.default_value,3) if isinstance(i.default_value,float) else '') for i in n.inputs if not i.is_linked and hasattr(i,'default_value') and isinstance(getattr(i,'default_value',None),float)][:6]
        print(' N',n.name,n.type,ex,ins)
    for l in m.node_tree.links: print(' L',l.from_node.name,l.from_socket.name,'->',l.to_node.name,l.to_socket.name)
