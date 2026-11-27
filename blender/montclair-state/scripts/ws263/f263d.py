# ws263 (merge208 CHAIN, after f263c): the pale tone between the police-lawn grass blades is mostly WS68's leaf-litter layer
# (WR_litter_bsdf, masked to the wooded slope N of the police building; probe263p: the visible ground there is
# WS68_RHD_ground_northDTM, f263c layer present but the WR_litter_mix shader sits on top). Same W263 density mask -> litter
# Base Color multiplied toward a darker brown and mixed toward a dark humus/thatch tone, so grass growing through litter reads
# as a dark, damp floor (UNVERIFIED tone; 2020 ortho shows leafless trees + brown litter on that slope, mown lawn E of the police).
import bpy
TAG='F263D'; m=bpy.data.materials['WS68_Ground_ortho_grass_north2020']; N=m.node_tree.nodes; L=m.node_tree.links
if 'W263_litter_mix' in N: raise SystemExit('F263D already')
lit=N['WR_litter_bsdf']; lk=lit.inputs['Base Color'].links[0]; src=lk.from_socket; L.remove(lk)
fac=N['W263_fac']
mul=N.new('ShaderNodeMix'); mul.name='W263_litter_mul'; mul.data_type='RGBA'; mul.blend_type='MULTIPLY'
L.new(fac.outputs[0],mul.inputs['Factor']); L.new(src,mul.inputs['A']); mul.inputs['B'].default_value=(0.50,0.50,0.36,1)
k=N.new('ShaderNodeMath'); k.name='W263_fac_humus'; k.operation='MULTIPLY'; k.inputs[1].default_value=0.40; L.new(fac.outputs[0],k.inputs[0])
mx=N.new('ShaderNodeMix'); mx.name='W263_litter_mix'; mx.data_type='RGBA'; mx.blend_type='MIX'
L.new(k.outputs[0],mx.inputs['Factor']); L.new(mul.outputs['Result'],mx.inputs['A']); mx.inputs['B'].default_value=(0.045,0.042,0.022,1)
L.new(mx.outputs['Result'],lit.inputs['Base Color'])
print(TAG,'litter layer added, was fed by',src.node.name,flush=True)
