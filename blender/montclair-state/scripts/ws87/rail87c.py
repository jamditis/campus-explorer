import bpy,os
o=bpy.data.objects['WS35_Kasser_steps_pipe_handrails_slim_UNVERIFIED']
m=bpy.data.materials.get('WS87_handrail_maroon_JOEphoto') or bpy.data.materials['WS35_black_painted_steel'].copy()
m.name='WS87_handrail_maroon_JOEphoto'
b=m.node_tree.nodes.get('Principled BSDF')
if b: b.inputs['Base Color'].default_value=(0.20,0.035,0.03,1); b.inputs['Roughness'].default_value=0.45
for i,mm in enumerate(o.data.materials): o.data.materials[i]=m
o.name='WS35_Cole_steps_handrails_MAROON_JOEphoto20261112'
print('A87 rails maroon',b is not None)
if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('A87 saved')
