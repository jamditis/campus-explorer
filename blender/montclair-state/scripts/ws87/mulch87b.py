import bpy,os
isl=[o for o in bpy.data.objects if o.name.startswith('WS77_lot_median_island_MULCH')][0]
m=bpy.data.materials.get('WS87_median_mulch_dark_JOEphoto') or bpy.data.materials.new('WS87_median_mulch_dark_JOEphoto')
m.use_nodes=True; nt=m.node_tree; N=nt.nodes; L=nt.links
for n in list(N):
    if n.type not in ('BSDF_PRINCIPLED','OUTPUT_MATERIAL'): N.remove(n)
b=N['Principled BSDF']; b.inputs['Roughness'].default_value=0.95
tc=N.new('ShaderNodeTexCoord'); nz=N.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value=9.0; nz.inputs['Detail'].default_value=8
L.new(tc.outputs['Object'],nz.inputs['Vector'])
cr=N.new('ShaderNodeValToRGB'); cr.color_ramp.elements[0].color=(0.035,0.022,0.015,1); cr.color_ramp.elements[1].color=(0.11,0.07,0.045,1)
L.new(nz.outputs['Fac'],cr.inputs['Fac']); L.new(cr.outputs['Color'],b.inputs['Base Color'])
bp=N.new('ShaderNodeBump'); bp.inputs['Strength'].default_value=0.5; L.new(nz.outputs['Fac'],bp.inputs['Height']); L.new(bp.outputs['Normal'],b.inputs['Normal'])
for i,mm in enumerate(isl.data.materials):
    if mm and 'Mulch' in mm.name: isl.data.materials[i]=m; print('A87 slot',i,'dark mulch')
if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('A87 saved')
