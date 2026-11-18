import bpy
m=bpy.data.materials['TZ_Cole_add_glass_UNVERIFIED']
b=[n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'][0]
print('USERS',m.users)
b.inputs['Base Color'].default_value=(0.06,0.07,0.08,1); b.inputs['Metallic'].default_value=0.4; b.inputs['Roughness'].default_value=0.03
b.inputs['Coat Weight'].default_value=0.3 if 'Coat Weight' in b.inputs else 0
bpy.ops.wm.save_mainfile(); print('SAVED')
