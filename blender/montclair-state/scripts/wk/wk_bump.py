import bpy, os
mt=bpy.data.materials['WH_east_dorm_patch_tone_UNVERIFIED']; N=mt.node_tree.nodes; L=mt.node_tree.links
P=N['Principled BSDF']; nr=N['WH_nrmix']; tc=N['EP_tc']; ff=N['WK_fac']
for nm in ['WK_vor','WK_bump_h','WK_bump']:
    if nm in N: N.remove(N[nm])
v=N.new('ShaderNodeTexVoronoi'); v.name='WK_vor'; v.inputs['Scale'].default_value=22; v.feature='DISTANCE_TO_EDGE'
L.new(tc.outputs['Object'],v.inputs['Vector'])
h=N.new('ShaderNodeMath'); h.name='WK_bump_h'; h.operation='MULTIPLY'; L.new(v.outputs['Distance'],h.inputs[0]); L.new(ff.outputs[0],h.inputs[1])
b=N.new('ShaderNodeBump'); b.name='WK_bump'; b.inputs['Strength'].default_value=0.45; b.inputs['Distance'].default_value=0.02
L.new(h.outputs[0],b.inputs['Height']); L.new(nr.outputs['Result'],b.inputs['Normal']); L.new(b.outputs['Normal'],P.inputs['Normal'])
# leaf-edge darkening in the colour: voronoi edge -> ramp fac nudge
mx=N['WK_noise_mix']
e=N.new('ShaderNodeMath'); e.name='WK_vor_tone'; e.operation='MULTIPLY_ADD'
L.new(v.outputs['Distance'],e.inputs[0]); e.inputs[1].default_value=0.6; L.new(mx.outputs[0],e.inputs[2])
L.new(e.outputs[0],N['WK_litter_ramp'].inputs['Fac'])
print('BUMP_OK')
if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')
