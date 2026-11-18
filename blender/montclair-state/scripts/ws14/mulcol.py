import bpy
m=bpy.data.materials['TZ_Cole_add_mullion_UNVERIFIED']; b=[n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'][0]
b.inputs['Base Color'].default_value=(0.05,0.05,0.055,1); b.inputs['Metallic'].default_value=0.5; b.inputs['Roughness'].default_value=0.4
bpy.ops.wm.save_mainfile(); print('SAVED')
