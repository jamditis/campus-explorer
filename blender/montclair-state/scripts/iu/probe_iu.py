import bpy
for nm in ['hn_amphi_seat_stone_blocks','hn_amphi_riser_coursed_stone']:
    m=bpy.data.materials[nm]; nt=m.node_tree; print('MAT',nm,len(nt.nodes))
    for q in nt.nodes:
        ins=[(i.name,round(i.default_value,3) if isinstance(i.default_value,float) else None) for i in q.inputs if not i.is_linked and hasattr(i,'default_value') and isinstance(getattr(i,'default_value',None),float)][:6]
        print(' N',q.name,q.bl_idname,q.label,ins)
    for l in nt.links: print(' L',l.from_node.name,l.from_socket.name,'->',l.to_node.name,l.to_socket.name)
