# qx: scored-concrete plaza material for the QXP pedestrian-area paving (world-aligned 2.0 x 2.0 m saw-cut grid, per-panel tone,
# grime noise). Generic, UNVERIFIED (no photo of the Student Center plaza surface). REVERT=1 restores the Footpaths_OSM material.
import bpy,os
MN='QXP_plaza_scored_concrete_UNVERIFIED'
obs=[o for o in bpy.data.objects if o.name.startswith('QXP_pedestrian_area_')]
fpm=bpy.data.objects['Footpaths_OSM'].material_slots[0].material
if os.environ.get('REVERT')=='1':
    for o in obs: o.data.materials[0]=fpm
    m=bpy.data.materials.get(MN)
    if m: bpy.data.materials.remove(m)
    print('QXM reverted')
else:
    m=bpy.data.materials.get(MN) or bpy.data.materials.new(MN); m.use_nodes=True; N=m.node_tree.nodes; L=m.node_tree.links; N.clear()
    out=N.new('ShaderNodeOutputMaterial'); bs=N.new('ShaderNodeBsdfPrincipled'); L.new(bs.outputs[0],out.inputs[0])
    tc=N.new('ShaderNodeTexCoord'); br=N.new('ShaderNodeTexBrick')
    br.offset=0.0; br.inputs['Scale'].default_value=0.5; br.inputs['Mortar Size'].default_value=0.006; br.inputs['Brick Width'].default_value=1.0; br.inputs['Row Height'].default_value=1.0
    br.inputs['Color1'].default_value=(0.25,0.245,0.23,1); br.inputs['Color2'].default_value=(0.29,0.285,0.27,1); br.inputs['Mortar'].default_value=(0.10,0.095,0.09,1)
    L.new(tc.outputs['Object'],br.inputs['Vector'])
    nz=N.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value=0.35; nz.inputs['Detail'].default_value=6; L.new(tc.outputs['Object'],nz.inputs['Vector'])
    fn=N.new('ShaderNodeTexNoise'); fn.inputs['Scale'].default_value=9.0; fn.inputs['Detail'].default_value=4; L.new(tc.outputs['Object'],fn.inputs['Vector'])
    mx=N.new('ShaderNodeMix'); mx.data_type='RGBA'; mx.blend_type='MULTIPLY'; mx.inputs['Factor'].default_value=0.55
    L.new(br.outputs['Color'],mx.inputs['A']); L.new(nz.outputs['Color'],mx.inputs['B'])
    mr=N.new('ShaderNodeMapRange'); mr.inputs['To Min'].default_value=0.88; mr.inputs['To Max'].default_value=1.06; L.new(fn.outputs['Fac'],mr.inputs['Value'])
    mx2=N.new('ShaderNodeMix'); mx2.data_type='RGBA'; mx2.blend_type='MULTIPLY'; mx2.inputs['Factor'].default_value=1.0
    L.new(mx.outputs['Result'],mx2.inputs['A']); cv=N.new('ShaderNodeCombineXYZ'); 
    for i in range(3): L.new(mr.outputs[0],cv.inputs[i])
    L.new(cv.outputs[0],mx2.inputs['B']); L.new(mx2.outputs['Result'],bs.inputs['Base Color'])
    bs.inputs['Roughness'].default_value=0.86
    bp=N.new('ShaderNodeBump'); bp.inputs['Strength'].default_value=0.25; bp.invert=True; L.new(br.outputs['Fac'],bp.inputs['Height']); L.new(bp.outputs[0],bs.inputs['Normal'])
    for o in obs: o.data.materials[0]=m
    print('QXM applied',len(obs))
if os.environ.get('QXSAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')
