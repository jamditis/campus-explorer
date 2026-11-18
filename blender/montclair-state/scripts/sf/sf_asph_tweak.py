import bpy
m=bpy.data.materials['SF_asphalt_worn_UNVERIFIED']; N=m.node_tree.nodes; b=N['Principled BSDF']
b.inputs['Roughness'].default_value=0.95; b.inputs['Specular IOR Level'].default_value=0.25
cr=[n for n in N if n.type=='VALTORGB'][0]; cr.color_ramp.elements[0].color=(0.05,0.05,0.052,1); cr.color_ramp.elements[1].color=(0.11,0.108,0.102,1)
bpy.ops.wm.save_mainfile(); print('SF_TWEAK_SAVED')
