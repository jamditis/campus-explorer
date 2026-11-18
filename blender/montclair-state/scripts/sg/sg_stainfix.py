# sg stain fix (~4:42 PM ET): the spherical gradient was off-centre (UV centre 0.5,0.5), so the stain showed as a ring outline.
# Re-centre: UV - 0.5, x2 -> gradient 1 at the centre, 0 at the rim. Material SG_oil_stain_UNVERIFIED only (removed by sg revert).
import bpy, os
m=bpy.data.materials['SG_oil_stain_UNVERIFIED']; N=m.node_tree.nodes; L=m.node_tree.links
tc=[n for n in N if n.type=='TEX_COORD'][0]; gr=[n for n in N if n.type=='TEX_GRADIENT'][0]
for l in list(gr.inputs['Vector'].links): L.remove(l)
vs=N.new('ShaderNodeVectorMath'); vs.operation='SUBTRACT'; vs.inputs[1].default_value=(0.5,0.5,0)
vm=N.new('ShaderNodeVectorMath'); vm.operation='SCALE'; vm.inputs['Scale'].default_value=2.0
L.new(tc.outputs['UV'],vs.inputs[0]); L.new(vs.outputs[0],vm.inputs[0]); L.new(vm.outputs[0],gr.inputs['Vector'])
mr=[n for n in N if n.type=='MAP_RANGE'][0]; mr.inputs['From Min'].default_value=0.02; mr.inputs['From Max'].default_value=0.35; mr.inputs['To Max'].default_value=0.7
print('SG stainfix ok')
if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')
