import bpy
mat=bpy.data.materials['WS18_sill_drip_stain_UNVERIFIED']; nt=mat.node_tree; L=nt.links
mx=[n for n in nt.nodes if n.type=='MATH' and n.operation=='MULTIPLY' and not n.inputs[1].is_linked][0]
mx.inputs[1].default_value=0.42
tc=[n for n in nt.nodes if n.type=='TEX_COORD'][0]
mp2=nt.nodes.new('ShaderNodeMapping'); mp2.inputs['Scale'].default_value=(5,0.2,1); L.new(tc.outputs['UV'],mp2.inputs['Vector'])
n2=nt.nodes.new('ShaderNodeTexNoise'); n2.inputs['Scale'].default_value=1.0; L.new(mp2.outputs[0],n2.inputs['Vector'])
r2=nt.nodes.new('ShaderNodeMapRange'); r2.inputs['From Min'].default_value=0.35; r2.inputs['From Max'].default_value=0.65; L.new(n2.outputs['Fac'],r2.inputs['Value'])
m2=nt.nodes.new('ShaderNodeMath'); m2.operation='MULTIPLY'
src=mx.inputs[0].links[0].from_socket
L.new(src,m2.inputs[0]); L.new(r2.outputs[0],m2.inputs[1]); L.new(m2.outputs[0],mx.inputs[0])
b=[n for n in nt.nodes if n.type=='BSDF_PRINCIPLED'][0]; b.inputs['Base Color'].default_value=(0.24,0.21,0.17,1)
bpy.ops.wm.save_mainfile(); print('SAVED')
