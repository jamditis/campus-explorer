# ws263 (merge208 CHAIN, after f263f): the grey film between blades at grazing angles is mostly sky specular off the ground
# (darker albedo barely changed it), so under the same W263 mask push Roughness toward 1.0 and Specular IOR Level 0.5 -> 0.1
# on the main Principled BSDF of both materials (damp thatch is matte).
import bpy
TAG='F263G'
for mn in ('WS68_Ground_ortho_grass_north2020','North_ground_ortho2020.001'):
    nt=bpy.data.materials[mn].node_tree; N=nt.nodes; L=nt.links
    if 'W263_rough_mix' in N: continue
    b=N['Principled BSDF']; fac=N['W263_fac']
    rin=b.inputs['Roughness']; mx=N.new('ShaderNodeMix'); mx.name='W263_rough_mix'; mx.data_type='FLOAT'
    L.new(fac.outputs[0],mx.inputs['Factor'])
    if rin.is_linked: src=rin.links[0].from_socket; L.remove(rin.links[0]); L.new(src,mx.inputs['A'])
    else: mx.inputs['A'].default_value=rin.default_value
    mx.inputs['B'].default_value=1.0; L.new(mx.outputs['Result'],rin)
    sin=b.inputs['Specular IOR Level']; sp=N.new('ShaderNodeMix'); sp.name='W263_spec_mix'; sp.data_type='FLOAT'
    L.new(fac.outputs[0],sp.inputs['Factor'])
    if sin.is_linked: src=sin.links[0].from_socket; L.remove(sin.links[0]); L.new(src,sp.inputs['A'])
    else: sp.inputs['A'].default_value=sin.default_value
    sp.inputs['B'].default_value=0.1; L.new(sp.outputs['Result'],sin)
    print(TAG,mn,'rough linked',mx.inputs['A'].is_linked,'spec A',sp.inputs['A'].is_linked or sp.inputs['A'].default_value,flush=True)
