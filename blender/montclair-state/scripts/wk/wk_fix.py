"""wk: leaf-litter woodland floor on the east-dorm LiDAR patches in the south stream ravine.
Mask = OSM natural=wood 315835594 AND 2017 B17 J5D6 CHM canopy (>3 m) fraction over 9 m > 0.35..0.65, gauss 2.8 m, limited to y<=362 (fade 350-362)."""
import bpy, numpy as np, json
z=np.load('/workspace/nj-scenes/montclair-state/data/wk/litter_mask.npz'); M=z['m']; X0,X1,Y0,Y1,_=z['extent']
ny,nx=M.shape
def samp(x,y):
    fx=x-X0-.5; fy=y-Y0-.5
    if fx<0 or fy<0 or fx>nx-1.001 or fy>ny-1.001: return 0.0
    i=int(fx); j=int(fy); a=fx-i; b=fy-j
    v=M[j,i]*(1-a)*(1-b)+M[j,i+1]*a*(1-b)+M[j+1,i]*(1-a)*b+M[j+1,i+1]*a*b
    w=min(1,max(0,(362-y)/12)); return float(v*w)
rep={}
for n in ['WJ_south_gully_LiDAR_patch_ext_UNVERIFIED','WF_east_dorm_LiDAR_terrain_patch_UNVERIFIED']:
    o=bpy.data.objects[n]; me=o.data; mw=o.matrix_world
    at=me.attributes.get('wk_litter') or me.attributes.new('wk_litter','FLOAT','POINT')
    vals=[samp(*(mw@v.co).xy) for v in me.vertices]
    at.data.foreach_set('value',vals)
    rep[n]=dict(n=len(vals),gt05=sum(v>.5 for v in vals),gt005=sum(v>.05 for v in vals))
    o['wk_obj']=1
mt=bpy.data.materials['WH_east_dorm_patch_tone_UNVERIFIED']; nt=mt.node_tree; N=nt.nodes; L=nt.links
users=[o.name for o in bpy.data.objects if o.type=='MESH' and any(s.material==mt for s in o.material_slots)]
rep['mat_users']=users
src=N['Mix']; hz=N['EP_haze_mix']
hzin=[i for i in hz.inputs if i.is_linked and i.links[0].from_node==src][0]
srcout=hzin.links[0].from_socket
for nm in [x.name for x in N if x.name.startswith('WK_')]: N.remove(N[nm])
A=N.new('ShaderNodeAttribute'); A.name='WK_litter_attr'; A.attribute_name='wk_litter'; A.attribute_type='GEOMETRY'
tc=N['EP_tc']
n1=N.new('ShaderNodeTexNoise'); n1.name='WK_leaf_noise'; n1.inputs['Scale'].default_value=0.9; n1.inputs['Detail'].default_value=6; n1.inputs['Roughness'].default_value=0.65
L.new(tc.outputs['Object'],n1.inputs['Vector'])
n2=N.new('ShaderNodeTexNoise'); n2.name='WK_leaf_fine'; n2.inputs['Scale'].default_value=14; n2.inputs['Detail'].default_value=3
L.new(tc.outputs['Object'],n2.inputs['Vector'])
cr=N.new('ShaderNodeValToRGB'); cr.name='WK_litter_ramp'
e=cr.color_ramp.elements; e[0].position=0.30; e[0].color=(0.060,0.042,0.026,1); e[1].position=0.72; e[1].color=(0.150,0.092,0.048,1)
e2=e.new(0.52); e2.color=(0.110,0.070,0.035,1)
mx=N.new('ShaderNodeMath'); mx.name='WK_noise_mix'; mx.operation='MULTIPLY_ADD'
L.new(n1.outputs['Fac'],mx.inputs[0]); mx.inputs[1].default_value=0.7
f2=N.new('ShaderNodeMath'); f2.name='WK_fine_w'; f2.operation='MULTIPLY'; L.new(n2.outputs['Fac'],f2.inputs[0]); f2.inputs[1].default_value=0.3
L.new(f2.outputs[0],mx.inputs[2]); L.new(mx.outputs[0],cr.inputs['Fac'])
# factor = smooth(litter) * (0.8 + 0.2*noise)
fm=N.new('ShaderNodeMapRange'); fm.name='WK_fac_mr'; fm.inputs['From Min'].default_value=0.05; fm.inputs['From Max'].default_value=0.8; fm.interpolation_type='SMOOTHSTEP'
L.new(A.outputs['Fac'],fm.inputs['Value'])
fb=N.new('ShaderNodeMath'); fb.name='WK_fac_break'; fb.operation='MULTIPLY_ADD'; L.new(n1.outputs['Fac'],fb.inputs[0]); fb.inputs[1].default_value=0.35; fb.inputs[2].default_value=0.75
ff=N.new('ShaderNodeMath'); ff.name='WK_fac'; ff.operation='MULTIPLY'; ff.use_clamp=True; L.new(fm.outputs['Result'],ff.inputs[0]); L.new(fb.outputs[0],ff.inputs[1])
mix=N.new('ShaderNodeMix'); mix.name='WK_litter_mix'; mix.data_type='RGBA'
L.new(ff.outputs[0],mix.inputs[0]); L.new(srcout,mix.inputs[6]); L.new(cr.outputs['Color'],mix.inputs[7])
L.new(mix.outputs[2],hzin)
# roughness up a touch under litter
P=N['Principled BSDF']
rr=N.new('ShaderNodeMapRange'); rr.name='WK_rough'; L.new(ff.outputs[0],rr.inputs['Value']); rr.inputs['To Min'].default_value=P.inputs['Roughness'].default_value; rr.inputs['To Max'].default_value=0.95
if not P.inputs['Roughness'].is_linked: L.new(rr.outputs['Result'],P.inputs['Roughness'])
mt['wk_mat']=1; mt['UNVERIFIED_wk']='wk: leaf-litter floor tone (procedural brown, colours UNVERIFIED) under OSM wood + LiDAR canopy in the south ravine'
rep['haze_A_from']=[l.from_node.name for l in hzin.links]; rep['hzin']=hzin.identifier
json.dump(rep,open('/workspace/nj-scenes/montclair-state/data/wk/fix_report.json','w'),indent=1); print(rep)
if __import__('os').environ.get('SAVE')=='1':
    bpy.ops.wm.save_mainfile(); print('SAVED')
