import bpy
nt=bpy.data.materials['OW2_Context_skirt_ortho_strip_tone_UNVERIFIED'].node_tree; N=nt.nodes
N['WJ_nz1'].inputs['Scale'].default_value=0.5
f1=N['WJ_f1']; f1.inputs[3].default_value=0.68; f1.inputs[4].default_value=1.12
f2=N['WJ_f2']; f2.inputs[3].default_value=0.86; f2.inputs[4].default_value=1.08
N['WJ_road'].inputs[4].default_value=0.78
# warm straw tint where the coarse noise is bright (dry patches), greener where dark
t=N['WJ_tint']; L=nt.links
hi=N.new('ShaderNodeMapRange'); hi.name=hi.label='WJ_dry'; hi.location=(1000,-2000)
hi.inputs[1].default_value=0.55; hi.inputs[2].default_value=0.68; hi.inputs[3].default_value=0.0; hi.inputs[4].default_value=0.7
L.new(N['WJ_nz1'].outputs['Fac'],hi.inputs[0])
dry=N.new('ShaderNodeMix'); dry.name=dry.label='WJ_drymix'; dry.data_type='RGBA'; dry.location=(1200,-2000)
dry.inputs['A'].default_value=(0.95,1.0,0.88,1); dry.inputs['B'].default_value=(1.06,1.0,0.78,1)
L.new(hi.outputs[0],dry.inputs['Factor']); L.new(dry.outputs['Result'],t.inputs['B'])
bpy.ops.wm.save_mainfile(); print('SAVED')
