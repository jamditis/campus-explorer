import bpy
for mn in ('OW2_Context_skirt_ortho_strip_tone_UNVERIFIED','BD_farfield_ortho_haze_bm'):
    b=bpy.data.materials[mn].node_tree.nodes['Principled BSDF']
    print('B',mn,[(i.name,round(i.default_value,3)) for i in b.inputs if i.name in ('Specular IOR Level','Roughness','Sheen Weight','Coat Weight','Subsurface Weight','Emission Strength')])
w=bpy.context.scene.world; print('W',w.name,[n.type for n in w.node_tree.nodes])
