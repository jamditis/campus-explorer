import bpy
for n in ['Roof_tile_or_membrane','PI_Feliciano_roof_tile_forced_UNVERIFIED','WS16_Barrel_tile_terracotta_plain','Eave_tile_top_soffit_under','TX_Partridge_precast_concrete_UNVERIFIED','TX_Partridge_brown_brick_UNVERIFIED']:
    m=bpy.data.materials[n]; print('MAT',n)
    for nd in m.node_tree.nodes:
        extra=''
        if nd.type=='ATTRIBUTE': extra=nd.attribute_name
        if nd.type=='BSDF_PRINCIPLED': extra=str([round(x,3) for x in nd.inputs['Base Color'].default_value])+' r'+str(round(nd.inputs['Roughness'].default_value,2))
        if nd.type=='VALTORGB': extra=str([[round(x,3) for x in e.color] for e in nd.color_ramp.elements])
        if nd.type=='TEX_IMAGE' and nd.image: extra=nd.image.name
        print('  ',nd.type,nd.name,extra)
# who uses PI_Feliciano forced
print([o.name for o in bpy.data.objects if o.type=='MESH' and any(s.material and s.material.name=='PI_Feliciano_roof_tile_forced_UNVERIFIED' for s in o.material_slots)][:16])
