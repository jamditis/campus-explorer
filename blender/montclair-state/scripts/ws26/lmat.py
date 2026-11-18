import bpy
for n in ['MI_Annex_letter_red','MI_Annex_letter_white','MI_Annex_letter_black']:
    m=bpy.data.materials[n]; 
    for nd in m.node_tree.nodes:
        if nd.type=='BSDF_PRINCIPLED': print('MAT',n,tuple(round(x,3) for x in nd.inputs['Base Color'].default_value),'em',tuple(round(x,3) for x in nd.inputs['Emission Color'].default_value),nd.inputs['Emission Strength'].default_value, 'rough',nd.inputs['Roughness'].default_value, [l.from_node.type for l in m.node_tree.links if l.to_node==nd])
