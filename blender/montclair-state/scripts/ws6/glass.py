import bpy
m=bpy.data.materials.new('WS6_Glass_dark_reflective_UNVERIFIED'); m.use_nodes=True
b=m.node_tree.nodes['Principled BSDF']
b.inputs['Base Color'].default_value=(0.012,0.016,0.02,1); b.inputs['Roughness'].default_value=0.035
b.inputs['IOR'].default_value=1.52
w=bpy.data.objects['WS6_Cole_gable_arched_window_UNVERIFIED']
w.data.materials[0]=m
bpy.ops.wm.save_mainfile(); print('SAVED')
