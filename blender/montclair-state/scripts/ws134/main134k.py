# ws134k: own UV-mapped cream modular brick for the Balance Kitchen massing (Freeman's cream-brick materials use
# generated coords and stripe on this mesh). Colour matched to Freeman's cream brick; UNVERIFIED for the dining hall.
import bpy, os
SAVE=os.environ.get('SAVE','0')=='1'
m=bpy.data.materials.get('WS134_cream_brick_modular_UV_UNVERIFIED') or bpy.data.materials.new('WS134_cream_brick_modular_UV_UNVERIFIED')
m.use_nodes=True; nt=m.node_tree; nt.nodes.clear()
out=nt.nodes.new('ShaderNodeOutputMaterial'); bs=nt.nodes.new('ShaderNodeBsdfPrincipled'); br=nt.nodes.new('ShaderNodeTexBrick'); uv=nt.nodes.new('ShaderNodeUVMap'); nz=nt.nodes.new('ShaderNodeTexNoise'); mx=nt.nodes.new('ShaderNodeMix'); bump=nt.nodes.new('ShaderNodeBump')
uv.uv_map='UVMap'; br.offset=0.5; br.inputs['Scale'].default_value=1.0; br.inputs['Brick Width'].default_value=0.203; br.inputs['Row Height'].default_value=0.0677
br.inputs['Mortar Size'].default_value=0.009; br.inputs['Color1'].default_value=(0.74,0.66,0.52,1); br.inputs['Color2'].default_value=(0.69,0.61,0.48,1); br.inputs['Mortar'].default_value=(0.62,0.60,0.56,1)
nz.inputs['Scale'].default_value=3.0; mx.data_type='RGBA'; mx.inputs['Factor'].default_value=0.12
nt.links.new(uv.outputs['UV'],br.inputs['Vector']); nt.links.new(br.outputs['Color'],mx.inputs[6]); nt.links.new(nz.outputs['Color'],mx.inputs[7])
nt.links.new(mx.outputs[2],bs.inputs['Base Color']); bs.inputs['Roughness'].default_value=0.85
bump.inputs['Strength'].default_value=0.25; nt.links.new(br.outputs['Fac'],bump.inputs['Height']); nt.links.new(bump.outputs['Normal'],bs.inputs['Normal'])
nt.links.new(bs.outputs['BSDF'],out.inputs['Surface'])
o=[o for o in bpy.data.objects if o.name.startswith('WS134_Balance_Kitchen')][0]; o.data.materials[0]=m
print('MAT set',o.data.materials[0].name)
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
