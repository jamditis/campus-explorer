import bpy
m=bpy.data.materials.new('WS16_Barrel_tile_terracotta_plain'); m.use_nodes=True
b=m.node_tree.nodes['Principled BSDF']; b.inputs['Base Color'].default_value=(0.45,0.14,0.07,1); b.inputs['Roughness'].default_value=0.62
nt=m.node_tree; nz=nt.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value=3.0
mx=nt.nodes.new('ShaderNodeMix'); mx.data_type='RGBA'; mx.inputs['A'].default_value=(0.38,0.11,0.055,1); mx.inputs['B'].default_value=(0.52,0.18,0.09,1)
nt.links.new(nz.outputs['Fac'],mx.inputs['Factor']); nt.links.new(mx.outputs['Result'],b.inputs['Base Color'])
o=bpy.data.objects['WS16_Cole_addition_barrel_eave_course_UNVERIFIED']; o.data.materials[0]=m
bpy.ops.wm.save_mainfile(); print('SAVED')
