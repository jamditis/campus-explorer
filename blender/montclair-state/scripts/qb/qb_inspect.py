import bpy
for on in ('Context_skirt_3DEP_ortho_4km','PZ_Feliciano_SW_DTM_edge_feather_UNVERIFIED','PK_Feliciano_west_DTM_fill_UNVERIFIED','Terrain_LiDAR_DTM_1m'):
    o=bpy.data.objects[on]; print('OBJ',on,'uv',[u.name for u in o.data.uv_layers],'attrs',[a.name for a in o.data.attributes][:12],'mods',[m.name for m in o.modifiers],'mats',[m.name if m else None for m in o.data.materials][:4], 'objmats',[s.link+':'+(s.material.name if s.material else '') for s in o.material_slots][:4])
for mn in ('Ground_ortho_grass',):
    pass
seen=set()
for on in ('Context_skirt_3DEP_ortho_4km','PZ_Feliciano_SW_DTM_edge_feather_UNVERIFIED'):
    for s in bpy.data.objects[on].material_slots:
        m=s.material
        if not m or m.name in seen: continue
        seen.add(m.name); print('MAT',m.name)
        for n in m.node_tree.nodes:
            ex=''
            if n.type=='TEX_IMAGE': ex=n.image.name if n.image else ''
            if n.type=='UVMAP': ex=n.uv_map
            if n.type=='ATTRIBUTE': ex=n.attribute_name
            ins=[(i.name, tuple(round(v,3) for v in i.default_value) if hasattr(i.default_value,'__len__') else round(i.default_value,3)) for i in n.inputs if not i.is_linked and hasattr(i,'default_value')][:4]
            print('  N',n.name,n.type,ex,ins)
        for l in m.node_tree.links: print('  L',l.from_node.name,l.from_socket.name,'->',l.to_node.name,l.to_socket.name)
exec(open('scripts/qa/qa_probe_strip.py').read())
