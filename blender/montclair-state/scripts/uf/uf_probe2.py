import bpy
for mn in ['TW_Cole_win_glass_UNVERIFIED','UE_Cole_arch_frame_dark_UNVERIFIED','UD_asphalt_worn_NormalAve_UNVERIFIED','SF_asphalt_worn_UNVERIFIED']:
    m=bpy.data.materials.get(mn)
    if not m: print('missing',mn); continue
    b=m.node_tree.nodes.get('Principled BSDF') if m.node_tree else None
    if not b: print(mn,'no principled'); continue
    keys=['Base Color','Roughness','Metallic','Transmission Weight','Alpha','IOR','Specular IOR Level']
    vals={}
    for k in keys:
        if k in b.inputs:
            vals[k]=tuple(round(x,3) for x in b.inputs[k].default_value) if hasattr(b.inputs[k].default_value,'__len__') else round(b.inputs[k].default_value,3)
    print(mn, vals, 'blend', m.blend_method)
# check UE collection
c=bpy.data.collections.get('UE_Cole_Hall_east_UNVERIFIED')
if c:
    print('UE col objs', [o.name for o in c.objects])
