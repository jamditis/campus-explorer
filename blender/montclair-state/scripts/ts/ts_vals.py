import bpy
m=bpy.data.materials['OW2_Context_skirt_ortho_strip_tone_UNVERIFIED']; N=m.node_tree.nodes
for nn in ('EP_canopy_col','EP_canopy_mix','EP_haze_mix','Mix','Mix.001','ah_leafon','QV_final','QV_ortho_tone'):
    n=N[nn]; print('V',nn,[(i.identifier,tuple(round(x,3) for x in i.default_value) if hasattr(i.default_value,'__len__') else round(i.default_value,3), i.is_linked) for i in n.inputs if i.enabled])
for nn in ('Attribute','Attribute.001'): print('A',nn,N[nn].attribute_name,N[nn].attribute_type)
me=bpy.data.objects['Context_skirt_3DEP_ortho_4km'].data; print('ATTRS',[(a.name,a.domain,a.data_type) for a in me.attributes])
