import bpy
for mn in ['MI_Annex_mural_arch_paint_UNVERIFIED','MH_Annex_coping_red_metal_photo2016','MH_Annex_CMU_painted_photo2016','MI_Annex_letter_red']:
    m=bpy.data.materials.get(mn); print('==',mn,m and m.users)
    if not m or not m.node_tree: continue
    for n in m.node_tree.nodes:
        vals={i.name:(tuple(round(x,3) for x in i.default_value) if hasattr(i.default_value,'__len__') else round(i.default_value,3)) for i in n.inputs if hasattr(i,'default_value') and not i.is_linked and i.name in('Base Color','Roughness','Color','Fac','Scale','Strength','Color1','Color2')}
        print(' ',n.type,n.name,vals, getattr(n,'image',None) and n.image.name)
        if n.type=='VALTORGB': print('   ramp',[(round(e.position,2),tuple(round(c,3) for c in e.color)) for e in n.color_ramp.elements])
    for l in m.node_tree.links: print('  L',l.from_node.name,l.from_socket.name,'->',l.to_node.name,l.to_socket.name)
o=[x for x in bpy.data.objects if x.name.startswith('MI Annex RED HAWK COUNTRY painted')][0]
me=o.data; print('niche obj',o.name,len(me.polygons),'uv',[u.name for u in me.uv_layers], 'attrs',[a.name for a in me.attributes])
for p in me.polygons[:16]: print(' f',p.index,[tuple(round(c,2) for c in (o.matrix_world@me.vertices[v].co)) for v in p.vertices][:4], len(p.vertices))
