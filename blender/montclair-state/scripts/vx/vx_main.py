"""vx: Blanton precast tone-down ('very white in sun') + subtle vertical weathering streaks. ALL UNVERIFIED (1981 slides 1051/1053 B/W; final colour unknown)."""
import bpy, json, os
STASH='/workspace/nj-scenes/montclair-state/data/vx/vx_ramp_stash.json'
K=float(os.environ.get('K','0.74'))
targets={'TN_precast_pier_UNVERIFIED':K,'TN_spandrel_band_UNVERIFIED':K,'TN_block_base_UNVERIFIED':0.92}
stash={}
for n,k in targets.items():
    m=bpy.data.materials[n]; nt=m.node_tree
    cr=nt.nodes['Color Ramp']
    stash[n]=[list(e.color) for e in cr.color_ramp.elements]
    for e in cr.color_ramp.elements:
        c=list(e.color); e.color=(c[0]*k,c[1]*k,c[2]*k*0.98,1.0)
    if n=='TN_block_base_UNVERIFIED': continue
    bsdf=nt.nodes['Principled BSDF']
    src=bsdf.inputs['Base Color'].links[0].from_socket
    tc=nt.nodes['Texture Coordinate']
    mp=nt.nodes.new('ShaderNodeMapping'); mp.name='VX_streak_map'; mp.inputs['Scale'].default_value=(6.0,6.0,0.35)
    nz=nt.nodes.new('ShaderNodeTexNoise'); nz.name='VX_streak_noise'; nz.inputs['Scale'].default_value=3.0; nz.inputs['Detail'].default_value=4.0
    mr=nt.nodes.new('ShaderNodeMapRange'); mr.name='VX_streak_range'
    mr.inputs['From Min'].default_value=0.35; mr.inputs['From Max'].default_value=0.65
    mr.inputs['To Min'].default_value=0.86; mr.inputs['To Max'].default_value=1.0
    mx=nt.nodes.new('ShaderNodeMix'); mx.name='VX_streak_mix'; mx.data_type='RGBA'; mx.blend_type='MULTIPLY'; mx.inputs[0].default_value=1.0
    nt.links.new(tc.outputs['Object'],mp.inputs['Vector'])
    nt.links.new(mp.outputs['Vector'],nz.inputs['Vector'])
    nt.links.new(nz.outputs['Fac'],mr.inputs['Value'])
    nt.links.new(src,mx.inputs[6])
    nt.links.new(mr.outputs['Result'],mx.inputs[7])
    nt.links.new(mx.outputs[2],bsdf.inputs['Base Color'])
    m['vx_mat']=1
json.dump(stash,open(STASH,'w'),indent=1)
bpy.ops.wm.save_mainfile()
print('VX saved', len(bpy.data.objects))
