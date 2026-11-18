import bpy
for o in bpy.data.objects:
    if 'Blanton' in o.name and o.type=='MESH':
        mats=[s.material.name if s.material else None for s in o.material_slots]
        print(o.name, 'hide' if o.hide_render else '', mats, round(o.dimensions.z,1))
seen=set()
for o in bpy.data.objects:
    if 'Blanton' in o.name:
        for s in o.material_slots:
            m=s.material
            if m and m.name not in seen and m.use_nodes:
                seen.add(m.name)
                b=m.node_tree.nodes.get('Principled BSDF')
                if b:
                    bc=b.inputs['Base Color']
                    print('MAT',m.name,tuple(round(x,3) for x in bc.default_value), 'linked' if bc.is_linked else '', 'rough',round(b.inputs['Roughness'].default_value,2), 'users',m.users)
