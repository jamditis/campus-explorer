import bpy
c=bpy.data.collections['RZ_StudentCenter_hero_from_north_UNVERIFIED']
seen=set()
for o in c.all_objects:
    for s in o.material_slots:
        m=s.material
        if not m or m.name in seen: continue
        seen.add(m.name); nt=m.node_tree
        b=[n for n in nt.nodes if n.type=='BSDF_PRINCIPLED']
        print('M',m.name,'| users',m.users,'| nodes',[n.type for n in nt.nodes],'| base',[tuple(round(x,2) for x in n.inputs['Base Color'].default_value) for n in b], 'linked',[n.inputs['Base Color'].is_linked for n in b], 'rough',[round(n.inputs['Roughness'].default_value,2) for n in b])
