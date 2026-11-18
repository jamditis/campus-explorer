import bpy
for mn in ('OV_Paving_concrete_walk_tone_UNVERIFIED','QT_walk_concrete_joints_UNVERIFIED','QXP_plaza_scored_concrete_UNVERIFIED'):
    m=bpy.data.materials[mn]
    us=[o.name for o in bpy.data.objects if o.type=='MESH' and any(s.material==m for s in o.material_slots)]
    print('MAT',mn,len(us),us[:12])
    for n in m.node_tree.nodes:
        vals={i.name:(tuple(round(v,3) for v in i.default_value) if hasattr(i.default_value,'__len__') else round(i.default_value,3)) for i in n.inputs if hasattr(i,'default_value') and not i.is_linked}
        print('  N',n.type,n.name,{k:v for k,v in vals.items() if k in ('Base Color','Color','Color1','Color2','Mortar','Roughness','Fac','Scale')})
        if n.type=='VALTORGB': print('   RAMP',[(round(e.position,2),tuple(round(c,3) for c in e.color)) for e in n.color_ramp.elements])
