# oh: second half of the sawtooth fix: Roof_tile_or_membrane also paints steep faces (normal z < 0.45, Math.039 -> Mix.009)
# grey; on the Schmitt mansard those are steep LiDAR triangles. Gate that switch with EM_inv (1 - em_ringforce) so faces with
# em_ringforce=1 (only Schmitt roof outside the og deck, set by oh_build) keep tile. Other users have no attr -> unchanged.
import bpy, os, sys
REV=os.environ.get('REVERT')=='1'
m=bpy.data.materials['Roof_tile_or_membrane']; nt=m.node_tree; N=nt.nodes; L=nt.links
g=N.get('OH_gate39'); m39=N['Math.039']; mix=N['Mix.009']
if g:
    L.new(m39.outputs[0],mix.inputs['Factor']); N.remove(g)
if not REV:
    g=N.new('ShaderNodeMath'); g.name='OH_gate39'; g.label='OH_gate39'; g.operation='MULTIPLY'
    L.new(m39.outputs[0],g.inputs[0]); L.new(N['EM_inv'].outputs[0],g.inputs[1]); L.new(g.outputs[0],mix.inputs['Factor'])
# oh v2: the real sawtooth: Math.003 (roofc ALPHA < 0.02 = 'ortho saw membrane') -> Math.038 picks the grey membrane texture;
# alpha interpolates across mansard triangles -> grey teeth. Gate it with EM_inv too.
g3=N.get('OH_gate03'); m03=N['Math.003']; m38=N['Math.038']
if g3:
    L.new(m03.outputs[0],m38.inputs[0]); N.remove(g3)
if not REV:
    g3=N.new('ShaderNodeMath'); g3.name='OH_gate03'; g3.label='OH_gate03'; g3.operation='MULTIPLY'
    L.new(m03.outputs[0],g3.inputs[0]); L.new(N['EM_inv'].outputs[0],g3.inputs[1]); L.new(g3.outputs[0],m38.inputs[0])
print('m38 in0 from',m38.inputs[0].links[0].from_node.name)
print('factor from',mix.inputs['Factor'].links[0].from_node.name)
if '--save' in sys.argv: bpy.ops.wm.save_mainfile(); print('SAVED')
