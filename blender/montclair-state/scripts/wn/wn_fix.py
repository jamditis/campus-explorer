"""wn (AO normal pointed straight down = proximity to the ground below; z gate disabled; minus upward-AO so inside corners and under-sill zones cancel): rain-splash grime on Stone Hall's lowest brick courses (shader-only, UNVERIFIED generic weathering).
AO proximity to ground/foundation x height gate (z<133.0) x vertical-streak noise -> multiply darken on base colour."""
import bpy, os
m=bpy.data.materials['TR_Stone_brick_detail_UNVERIFIED']; nt=m.node_tree; N=nt.nodes; L=nt.links
for n in [n for n in N if n.name.startswith('WN_')]: N.remove(n)
P=[n for n in N if n.type=='BSDF_PRINCIPLED'][0]
bc=P.inputs['Base Color']; src=bc.links[0].from_socket if bc.links else None
STR=float(os.environ.get('WN_STR','0.75'))
def nn(t,name,loc):
    n=N.new(t); n.name=name; n.label=name; n.location=(P.location.x-400+loc[0],P.location.y-600+loc[1]); return n
ao=nn('ShaderNodeAmbientOcclusion','WN_ao',(-800,0)); ao.samples=8; ao.only_local=False; ao.inputs['Distance'].default_value=0.9; ao.inputs['Normal'].default_value=(0,0,-1)
inv=nn('ShaderNodeMath','WN_ao_inv',(-600,0)); inv.operation='SUBTRACT'; inv.inputs[0].default_value=1.0; L.new(ao.outputs['AO'],inv.inputs[1])
ao2=nn('ShaderNodeAmbientOcclusion','WN_ao_up',(-800,200)); ao2.samples=8; ao2.only_local=False; ao2.inputs['Distance'].default_value=0.9; ao2.inputs['Normal'].default_value=(0,0,1)
inv2=nn('ShaderNodeMath','WN_ao_up_inv',(-600,200)); inv2.operation='SUBTRACT'; inv2.inputs[0].default_value=1.0; L.new(ao2.outputs['AO'],inv2.inputs[1])
dif=nn('ShaderNodeMath','WN_ao_diff',(-500,100)); dif.operation='SUBTRACT'; dif.use_clamp=True; upk=nn('ShaderNodeMath','WN_ao_up_k',(-550,250)); upk.operation='MULTIPLY'; upk.inputs[1].default_value=float(os.environ.get('WN_UPK','0.55')); L.new(inv2.outputs[0],upk.inputs[0])
L.new(inv.outputs[0],dif.inputs[0]); L.new(upk.outputs[0],dif.inputs[1])
aop=nn('ShaderNodeMath','WN_ao_pow',(-450,0)); aop.operation='POWER'; aop.inputs[1].default_value=0.6; aop.use_clamp=True; L.new(dif.outputs[0],aop.inputs[0])
geo=nn('ShaderNodeNewGeometry','WN_geo',(-800,-250))
sep=nn('ShaderNodeSeparateXYZ','WN_pos',(-600,-250)); L.new(geo.outputs['Position'],sep.inputs[0])
zr=nn('ShaderNodeMapRange','WN_zgate',(-450,-250)); zr.inputs['From Min'].default_value=1000.0; zr.inputs['From Max'].default_value=1001.0; zr.inputs['To Min'].default_value=2.4; zr.inputs['To Max'].default_value=0; zr.clamp=True
L.new(sep.outputs['Z'],zr.inputs['Value'])
sn=nn('ShaderNodeSeparateXYZ','WN_nrm',(-600,-450)); L.new(geo.outputs['Normal'],sn.inputs[0])
na=nn('ShaderNodeMath','WN_nabs',(-450,-450)); na.operation='ABSOLUTE'; L.new(sn.outputs['Z'],na.inputs[0])
nw=nn('ShaderNodeMath','WN_wall',(-300,-450)); nw.operation='LESS_THAN'; nw.inputs[1].default_value=0.5; L.new(na.outputs[0],nw.inputs[0])
mp=nn('ShaderNodeMapping','WN_streak_map',(-600,-650)); mp.inputs['Scale'].default_value=(22,22,2.5); L.new(geo.outputs['Position'],mp.inputs['Vector'])
nz=nn('ShaderNodeTexNoise','WN_streak',(-450,-650)); nz.inputs['Scale'].default_value=1.0; nz.inputs['Detail'].default_value=3; L.new(mp.outputs[0],nz.inputs['Vector'])
nr=nn('ShaderNodeMapRange','WN_streak_rng',(-300,-650)); nr.inputs['From Min'].default_value=0.3; nr.inputs['From Max'].default_value=0.7; nr.inputs['To Min'].default_value=0.45; nr.inputs['To Max'].default_value=1.0; nr.clamp=True; L.new(nz.outputs['Fac'],nr.inputs['Value'])
m1=nn('ShaderNodeMath','WN_m1',(-250,0)); m1.operation='MULTIPLY'; m1.use_clamp=True; L.new(aop.outputs[0],m1.inputs[0]); L.new(zr.outputs[0],m1.inputs[1])
m2=nn('ShaderNodeMath','WN_m2',(-150,-150)); m2.operation='MULTIPLY'; L.new(m1.outputs[0],m2.inputs[0]); L.new(nw.outputs[0],m2.inputs[1])
m3=nn('ShaderNodeMath','WN_m3',(-50,-300)); m3.operation='MULTIPLY'; L.new(m2.outputs[0],m3.inputs[0]); L.new(nr.outputs[0],m3.inputs[1])
m4=nn('ShaderNodeMath','WN_fac',(50,-300)); m4.operation='MULTIPLY'; m4.use_clamp=True; m4.inputs[1].default_value=STR; L.new(m3.outputs[0],m4.inputs[0])
mix=nn('ShaderNodeMix','WN_mix',(200,0)); mix.data_type='RGBA'; mix.blend_type='MULTIPLY'
L.new(m4.outputs[0],mix.inputs['Factor'])
if src: L.new(src,mix.inputs[6])
else: mix.inputs[6].default_value=bc.default_value
mix.inputs[7].default_value=(0.42,0.38,0.33,1)
L.new(mix.outputs[2],bc)
# slightly rougher/duller where grimy
rs=P.inputs['Roughness']
if not rs.links:
    ra=nn('ShaderNodeMath','WN_rough',(200,-200)); ra.operation='ADD'; ra.use_clamp=True; ra.inputs[0].default_value=rs.default_value
    rb=nn('ShaderNodeMath','WN_rough_k',(100,-200)); rb.operation='MULTIPLY'; rb.inputs[1].default_value=0.15; L.new(m4.outputs[0],rb.inputs[0]); L.new(rb.outputs[0],ra.inputs[1]); L.new(ra.outputs[0],rs)
print('WN nodes',len([n for n in N if n.name.startswith('WN_')]),'src',src and src.node.name,flush=True)
if os.environ.get('WN_SAVE')=='1':
    bpy.ops.wm.save_mainfile(); print('SAVED',len(bpy.data.objects),flush=True)
