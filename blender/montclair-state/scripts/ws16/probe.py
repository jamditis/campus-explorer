import bpy
for o in bpy.data.objects:
    n=o.name
    if ('Cole' in n) and o.type=='MESH':
        mats=[s.material.name if s.material else None for s in o.material_slots]
        print('OBJ',n,len(o.data.polygons),mats[:6])
def col(mn):
    m=bpy.data.materials.get(mn)
    if not m or not m.node_tree: return
    for nd in m.node_tree.nodes:
        if nd.type=='BSDF_PRINCIPLED':
            i=nd.inputs['Base Color']; print('MAT',mn,m.users,tuple(round(x,3) for x in i.default_value),'linked',i.is_linked, 'rough',round(nd.inputs['Roughness'].default_value,2))
        if nd.type in('RGB',): print('  RGB',mn,nd.name,tuple(round(x,3) for x in nd.outputs[0].default_value))
        if nd.type=='VALTORGB': print('  RAMP',mn,[tuple(round(x,3) for x in e.color) for e in nd.color_ramp.elements])
seen=set()
for o in bpy.data.objects:
    if 'Cole' in o.name and o.type=='MESH':
        for s in o.material_slots:
            if s.material and s.material.name not in seen: seen.add(s.material.name); col(s.material.name)
