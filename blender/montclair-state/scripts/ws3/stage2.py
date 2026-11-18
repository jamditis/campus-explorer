import bpy
conc=bpy.data.materials['WS3_Concrete_panels_sawcut']
old=bpy.data.materials['COLE_plaza_pavers_bs']; oldm=bpy.data.materials['COLE_planting_mulch_smooth_bu']
m=bpy.data.materials.new('WS3_Mulch_bark_dark_brown'); m.use_nodes=True; N=m.node_tree.nodes; L=m.node_tree.links
b=N['Principled BSDF']; geo=N.new('ShaderNodeNewGeometry')
n1=N.new('ShaderNodeTexNoise'); n1.inputs['Scale'].default_value=9; n1.inputs['Detail'].default_value=10; n1.inputs['Roughness'].default_value=0.7
L.new(geo.outputs['Position'],n1.inputs['Vector'])
r=N.new('ShaderNodeValToRGB'); r.color_ramp.elements[0].color=(0.075,0.045,0.028,1); r.color_ramp.elements[1].color=(0.21,0.13,0.075,1)
L.new(n1.outputs['Fac'],r.inputs[0]); L.new(r.outputs[0],b.inputs['Base Color']); b.inputs['Roughness'].default_value=0.96
n2=N.new('ShaderNodeTexNoise'); n2.inputs['Scale'].default_value=60; L.new(geo.outputs['Position'],n2.inputs['Vector'])
bu=N.new('ShaderNodeBump'); bu.inputs['Strength'].default_value=0.8; bu.inputs['Distance'].default_value=0.02
L.new(n2.outputs['Fac'],bu.inputs['Height']); L.new(bu.outputs[0],b.inputs['Normal'])
cnt={'pav':[], 'mulch':[]}
for o in bpy.data.objects:
  for s in o.material_slots:
    if s.material==old: s.material=conc; cnt['pav'].append(o.name)
    elif s.material==oldm: s.material=m; cnt['mulch'].append(o.name)
print('SWAP',cnt)
bpy.ops.wm.save_mainfile(); print('SAVED')
