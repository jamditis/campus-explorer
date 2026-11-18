"""wr: WM_litter_mask extended south to y140 (x120-320, y140-420). Reload packed image, retarget the two existing
readers' world-XY mapping (WH patch + WM_skirt_litter), and add a gated leaf-litter Mix Shader to the shared LiDAR
ground materials (Terrain_LiDAR_DTM_1m / QG / QH / QI) ONLY for y<240 so the floor under the WQ south-wood trees
matches the ravine woods. Outside the mask/gate the Mix fac is exactly 0 -> original shader unchanged."""
import bpy, os, json
R='/workspace/nj-scenes/montclair-state'; rep={}
PNG=f'{R}/data/wm/wm_litter_mask.png'
X0,Y0,SX,SY=120.,140.,200.,280.
old=bpy.data.images.get('WM_litter_mask'); users=[]
for mat in bpy.data.materials:
    if mat.use_nodes and mat.node_tree:
        for n in mat.node_tree.nodes:
            if old is not None and getattr(n,'image',None)==old: users.append((mat.name,n.name))
new=bpy.data.images.load(PNG); new.name='WM_litter_mask_wr'; new.colorspace_settings.name='Non-Color'; new.pack()
for mn,nn in users: bpy.data.materials[mn].node_tree.nodes[nn].image=new
if old: bpy.data.images.remove(old)
new.name='WM_litter_mask'; rep['img']=list(new.size); rep['users']=users
for mn,_ in users:
    mp=bpy.data.materials[mn].node_tree.nodes.get('WM_map')
    if mp:
        mp.inputs['Location'].default_value=(-X0/SX,-Y0/SY,0); mp.inputs['Scale'].default_value=(1/SX,1/SY,0)
        bpy.data.materials[mn]['wr_mat']=1
rep['remapped']=[mn for mn,_ in users]
wh=bpy.data.materials['WH_east_dorm_patch_tone_UNVERIFIED']; W=wh.node_tree.nodes
def add_litter(mat):
    nt=mat.node_tree; N=nt.nodes; L=nt.links
    for n in [x for x in N if x.name.startswith('WR_')]: N.remove(n)
    out=[n for n in N if n.bl_idname=='ShaderNodeOutputMaterial' and n.is_active_output] or [n for n in N if n.bl_idname=='ShaderNodeOutputMaterial']
    out=out[0]; src=out.inputs['Surface'].links[0].from_socket
    def cp(name,typ):
        n=N.new(typ); n.name='WR_'+name; o=W[name]
        for a in ('operation','interpolation_type','feature','data_type','use_clamp','noise_dimensions','distance','voronoi_dimensions'):
            if hasattr(o,a):
                try: setattr(n,a,getattr(o,a))
                except Exception: pass
        for a,b in zip(o.inputs,n.inputs):
            if hasattr(a,'default_value') and not a.is_linked:
                try: b.default_value=a.default_value
                except Exception: pass
        return n
    g=N.new('ShaderNodeNewGeometry'); g.name='WR_geo'
    mp=N.new('ShaderNodeMapping'); mp.name='WR_map'; mp.vector_type='POINT'
    mp.inputs['Location'].default_value=(-X0/SX,-Y0/SY,0); mp.inputs['Scale'].default_value=(1/SX,1/SY,0)
    L.new(g.outputs['Position'],mp.inputs['Vector'])
    t=N.new('ShaderNodeTexImage'); t.name='WR_mask'; t.image=new; t.extension='CLIP'; t.interpolation='Cubic'
    L.new(mp.outputs['Vector'],t.inputs['Vector'])
    sp=N.new('ShaderNodeSeparateXYZ'); sp.name='WR_sep'; L.new(g.outputs['Position'],sp.inputs['Vector'])
    yg=N.new('ShaderNodeMapRange'); yg.name='WR_ygate'; yg.clamp=True
    yg.inputs['From Min'].default_value=232; yg.inputs['From Max'].default_value=240
    yg.inputs['To Min'].default_value=1; yg.inputs['To Max'].default_value=0; L.new(sp.outputs['Y'],yg.inputs['Value'])
    tc=N.new('ShaderNodeTexCoord'); tc.name='WR_tc'
    n1=cp('WK_leaf_noise','ShaderNodeTexNoise'); n2=cp('WK_leaf_fine','ShaderNodeTexNoise')
    L.new(tc.outputs['Object'],n1.inputs['Vector']); L.new(tc.outputs['Object'],n2.inputs['Vector'])
    mx=cp('WK_noise_mix','ShaderNodeMath'); f2=cp('WK_fine_w','ShaderNodeMath')
    L.new(n1.outputs['Fac'],mx.inputs[0]); L.new(n2.outputs['Fac'],f2.inputs[0]); L.new(f2.outputs[0],mx.inputs[2])
    fm=cp('WK_fac_mr','ShaderNodeMapRange'); L.new(t.outputs['Color'],fm.inputs['Value'])
    fb=cp('WK_fac_break','ShaderNodeMath'); L.new(n1.outputs['Fac'],fb.inputs[0])
    ff=cp('WK_fac','ShaderNodeMath'); L.new(fm.outputs['Result'],ff.inputs[0]); L.new(fb.outputs[0],ff.inputs[1])
    fg=N.new('ShaderNodeMath'); fg.name='WR_fac_gated'; fg.operation='MULTIPLY'; fg.use_clamp=True
    L.new(ff.outputs[0],fg.inputs[0]); L.new(yg.outputs['Result'],fg.inputs[1])
    cr=N.new('ShaderNodeValToRGB'); cr.name='WR_WK_litter_ramp'; oe=W['WK_litter_ramp'].color_ramp.elements; e=cr.color_ramp.elements
    while len(e)<len(oe): e.new(0.5)
    for a,b in zip(oe,e): b.position=a.position; b.color=a.color
    v=cp('WK_vor','ShaderNodeTexVoronoi'); L.new(tc.outputs['Object'],v.inputs['Vector'])
    vt=cp('WK_vor_tone','ShaderNodeMath'); L.new(v.outputs['Distance'],vt.inputs[0]); L.new(mx.outputs[0],vt.inputs[2]); L.new(vt.outputs[0],cr.inputs['Fac'])
    h=cp('WK_bump_h','ShaderNodeMath'); L.new(v.outputs['Distance'],h.inputs[0]); L.new(fg.outputs[0],h.inputs[1])
    b=cp('WK_bump','ShaderNodeBump'); L.new(h.outputs[0],b.inputs['Height'])
    P=N.new('ShaderNodeBsdfPrincipled'); P.name='WR_litter_bsdf'
    L.new(cr.outputs['Color'],P.inputs['Base Color']); P.inputs['Roughness'].default_value=0.93
    L.new(b.outputs['Normal'],P.inputs['Normal'])
    ms=N.new('ShaderNodeMixShader'); ms.name='WR_litter_mix'
    L.new(fg.outputs[0],ms.inputs['Fac']); L.new(src,ms.inputs[1]); L.new(P.outputs['BSDF'],ms.inputs[2])
    L.new(ms.outputs['Shader'],out.inputs['Surface'])
    mat['wr_mat']=1; mat['UNVERIFIED_wr']='wr: leaf-litter mix from WM_litter_mask (OSM wood 315835594 AND 2017 CHM canopy, crown-gated), only y<240; fac 0 elsewhere'
    return src.node.name
TARGETS=['Ground_ortho_grass','Lawn_Varied_Oct_local_fade','COLE_lawn_post2020_bs','COLE_planting_mulch_bs']
rep['litter_added']={m:add_litter(bpy.data.materials[m]) for m in TARGETS}
json.dump(rep,open(f'{R}/data/wr/fix_report.json','w'),indent=1); print('REP',rep,flush=True)
if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED',flush=True)
if os.environ.get('CAMS'):
    exec(open(f'{R}/scripts/wr/wr_render.py').read())
