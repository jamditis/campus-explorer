# oj (Oct 31 2026): Schmitt pavilion follow-ups after oi: recessed side windows on both pavilion returns (exact boolean,
# red-brown frames, tinted glass, dark backing), tinted glass on the arch/doors/top grid, darker red-tile hip roof with
# course banding, lettering x1.12 in plane, warmer/less regular split-face block (shared Schmitt block + pier plinth mats),
# thin scored concrete landing pad over the OSM path seams at the doors (OSM plane NOT edited). All sizes UNVERIFIED.
# REVERT=1 restores the oi state. State -> data/oj/oj_state.json.  Usage: blender -b main --python oj_build.py -- --save
import bpy, bmesh, json, math, os, sys
from mathutils import Vector
REV=os.environ.get('REVERT')=='1'; SAVE='--save' in sys.argv
ROOT=os.path.dirname(bpy.data.filepath); SJ=os.path.join(ROOT,'data/oj/oj_state.json')
CN='OJ_Schmitt_pavilion_sides_glass_landing_20261031oj'
SHELL='OI_Schmitt_pavilion_shell_stucco'; LET='OI_Schmitt_lettering_CONRAD_J_SCHMITT_HALL'
BLK=['OH_Schmitt_stucco_block_base_UNVERIFIED','OI_Schmitt_pier_block_plinth_UNVERIFIED']
ROOFM='OI_Schmitt_pavilion_roof_tile_UNVERIFIED'
def restore_mesh(objname,key):
    o=bpy.data.objects[objname]; orig=bpy.data.meshes.get(key)
    if orig:
        cur=o.data; nm=cur.name; o.data=orig; bpy.data.meshes.remove(cur); orig.name=nm; orig.use_fake_user=False
# ---- undo ----
sc=bpy.context.scene
st=json.loads(sc['oj_state']) if 'oj_state' in sc else (json.load(open(SJ)) if os.path.exists(SJ) else {})
c=bpy.data.collections.get(CN)
if c:
    for ob in list(c.objects):
        me=ob.data; bpy.data.objects.remove(ob)
        if me and me.users==0 and isinstance(me,bpy.types.Mesh): bpy.data.meshes.remove(me)
    bpy.data.collections.remove(c)
restore_mesh(SHELL,'OJ_shell_orig_pre_oj'); restore_mesh(LET,'OJ_lettering_orig_pre_oj')
for on,mn in st.get('mats',{}).items():
    o=bpy.data.objects.get(on)
    if o: o.data.materials[0]=bpy.data.materials[mn]
for mn in BLK+[ROOFM]:
    m=bpy.data.materials.get(mn)
    if not m: continue
    nt=m.node_tree
    for k,v in st.get('vals',{}).get(mn,{}).items():
        nn,sock=k.split('|'); n=nt.nodes[nn]; s=n.inputs[sock]
        for l in list(s.links): nt.links.remove(l)
        s.default_value=v
    for n in [n for n in nt.nodes if n.name.startswith('OJ_')]: nt.nodes.remove(n)
    rl=st.get('relink',{}).get(mn)
    if rl:
        for fn,fs,tn,ts in rl: nt.links.new(nt.nodes[fn].outputs[fs],nt.nodes[tn].inputs[ts])
for n in [m.name for m in bpy.data.materials if m.name.startswith('OJ_Schmitt_')]: bpy.data.materials.remove(bpy.data.materials[n])
if os.path.exists(SJ): os.remove(SJ)
if 'oj_state' in sc: del sc['oj_state']
for on in ('OI_Schmitt_pavilion_arch_glass','OI_Schmitt_pavilion_top_window_glass'):
    o=bpy.data.objects[on]
    if o.data.materials[0] is None: o.data.materials[0]=bpy.data.materials['OH_Schmitt_door_glass_clear_UNVERIFIED']
if REV:
    print('REVERTED')
    if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
    raise SystemExit(0)
st={'mats':{},'vals':{},'relink':{},'note':'oj'}
fr=bpy.data.objects['OG_Schmitt_E_entrance_storefront_frame']; la=bpy.data.objects['OG_Schmitt_E_entrance_landing']
fv=[fr.matrix_world@v.co for v in fr.data.vertices]; lb=[la.matrix_world@v.co for v in la.data.vertices]
cen=sum(fv,Vector())/len(fv); lc=sum(lb,Vector())/len(lb)
OUT=Vector(((lc-cen).x,(lc-cen).y,0)).normalized(); AL=Vector((-OUT.y,OUT.x,0)); cen.z=0
def P(a,o,z): return cen+AL*a+OUT*o+Vector((0,0,z))
HA=3.80
col=bpy.data.collections.new(CN); bpy.context.scene.collection.children.link(col)
def newobj(name,bm,m):
    me=bpy.data.meshes.new(name); bm.to_mesh(me); bm.free(); me.materials.append(m)
    o=bpy.data.objects.new(name,me); col.objects.link(o); o['UNVERIFIED']='oj: style-consistent guess, no photo of the pavilion sides'; return o
def box(bm,a0,a1,o0,o1,z0,z1,zt=None):
    vs=[]
    for k,z in enumerate((z0,z1)):
        for a,o in ((a0,o0),(a1,o0),(a1,o1),(a0,o1)):
            zz=z if (k==0 or zt is None) else zt(o)
            vs.append(bm.verts.new(P(a,o,zz)))
    for f in ((0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)): bm.faces.new([vs[i] for i in f])
def mat(n,col_,rough=0.5,trans=0.0,ior=1.5):
    m=bpy.data.materials.new(n); m.use_nodes=True; p=m.node_tree.nodes['Principled BSDF']
    p.inputs['Base Color'].default_value=(*col_,1); p.inputs['Roughness'].default_value=rough
    if trans: p.inputs['Transmission Weight'].default_value=trans; p.inputs['IOR'].default_value=ior
    return m
M_red=bpy.data.materials['OH_Schmitt_win_frame_red_brown']
M_gl=mat('OJ_Schmitt_glass_tinted_UNVERIFIED',(0.60,0.68,0.68),0.02,1.0,1.52)
M_bk=mat('OJ_Schmitt_side_window_backing_dark_UNVERIFIED',(0.035,0.032,0.03),0.8)
# ---- 1 pavilion side windows: 3 storeys x 2 sides, recessed 0.15 into the 0.17 m skin (stays outside the bay walls at +-3.63) ----
O0,O1=-2.65,-1.35; FL=[(140.12,141.42),(142.78,144.58),(146.28,148.08)]
sh=bpy.data.objects[SHELL]; orig=sh.data.copy(); orig.name='OJ_shell_orig_pre_oj'; orig.use_fake_user=True
cb=bmesh.new()
for s in (1,-1):
    for z0,z1 in FL:
        a_in=s*(HA-0.15); a_out=s*(HA+0.5); box(cb,min(a_in,a_out),max(a_in,a_out),O0,O1,z0,z1)
bmesh.ops.recalc_face_normals(cb,faces=cb.faces)
cme=bpy.data.meshes.new('OJ_cut_tmp'); cb.to_mesh(cme); cb.free(); cut=bpy.data.objects.new('OJ_cut_tmp',cme); col.objects.link(cut)
md=sh.modifiers.new('ojcut','BOOLEAN'); md.operation='DIFFERENCE'; md.solver='EXACT'; md.object=cut
dg=bpy.context.evaluated_depsgraph_get(); nm=bpy.data.meshes.new_from_object(sh.evaluated_get(dg)); sh.modifiers.remove(md)
old=sh.data; sh.data=nm; bpy.data.meshes.remove(old); nm.name=SHELL
bpy.data.objects.remove(cut); bpy.data.meshes.remove(cme)
_b=bmesh.new(); _b.from_mesh(sh.data); print('shell faces',len(sh.data.polygons),'nonmanifold',sum(1 for e in _b.edges if not e.is_manifold)); _b.free()
bf=bmesh.new(); bg=bmesh.new(); bb=bmesh.new(); W=0.07
for s in (1,-1):
    def A(x0,x1): x0*=s; x1*=s; return min(x0,x1),max(x0,x1)
    for z0,z1 in FL:
        fa0,fa1=A(HA-0.12,HA-0.03)   # frame band depth (inside the recess, 3 cm behind the wall face)
        box(bf,fa0,fa1,O0,O0+W,z0,z1); box(bf,fa0,fa1,O1-W,O1,z0,z1)
        box(bf,fa0,fa1,O0+W,O1-W,z0,z0+0.09); box(bf,fa0,fa1,O0+W,O1-W,z1-W,z1)
        m0=(O0+O1)/2; box(bf,fa0,fa1,m0-0.03,m0+0.03,z0+0.09,z1-W)
        ga0,ga1=A(HA-0.085,HA-0.075); box(bg,ga0,ga1,O0+W,O1-W,z0+0.09,z1-W)
        ka0,ka1=A(HA-0.145,HA-0.135); box(bb,ka0,ka1,O0+0.01,O1-0.01,z0+0.01,z1-0.01)
        sa0,sa1=A(HA-0.03,HA+0.05); box(bf,sa0,sa1,O0-0.04,O1+0.04,z0-0.05,z0)   # small projecting sill
newobj('OJ_Schmitt_pavilion_side_window_frames',bf,M_red)
newobj('OJ_Schmitt_pavilion_side_window_glass',bg,M_gl)
newobj('OJ_Schmitt_pavilion_side_window_backing',bb,M_bk)
# ---- 2 tinted glass on arch/doors/top grid ----
for on in ('OI_Schmitt_pavilion_arch_glass','OI_Schmitt_pavilion_top_window_glass'):
    o=bpy.data.objects[on]; st['mats'][on]=o.data.materials[0].name; o.data.materials[0]=M_gl
# ---- 3 hip roof: darker red tile + course banding + variation ----
m=bpy.data.materials[ROOFM]; nt=m.node_tree; p=nt.nodes['Principled BSDF']
st['vals'][ROOFM]={'Principled BSDF|Base Color':list(p.inputs['Base Color'].default_value),'Principled BSDF|Roughness':p.inputs['Roughness'].default_value}
p.inputs['Roughness'].default_value=0.72
tc=nt.nodes.new('ShaderNodeTexCoord'); tc.name='OJ_tc'
wv=nt.nodes.new('ShaderNodeTexWave'); wv.name='OJ_wave'; wv.wave_type='BANDS'; wv.bands_direction='Z'; wv.inputs['Scale'].default_value=1.0/0.33*0.16; wv.inputs['Distortion'].default_value=0.4
nz=nt.nodes.new('ShaderNodeTexNoise'); nz.name='OJ_noise'; nz.inputs['Scale'].default_value=0.9
nt.links.new(tc.outputs['Object'],wv.inputs['Vector']); nt.links.new(tc.outputs['Object'],nz.inputs['Vector'])
cr=nt.nodes.new('ShaderNodeValToRGB'); cr.name='OJ_ramp'; cr.color_ramp.elements[0].color=(0.20,0.050,0.028,1); cr.color_ramp.elements[1].color=(0.31,0.085,0.042,1)
nt.links.new(nz.outputs['Fac'],cr.inputs['Fac'])
mx=nt.nodes.new('ShaderNodeMix'); mx.name='OJ_mix'; mx.data_type='RGBA'; mx.blend_type='MULTIPLY'; mx.inputs['Factor'].default_value=0.35
nt.links.new(cr.outputs['Color'],mx.inputs['A']); nt.links.new(wv.outputs['Color'],mx.inputs['B'])
nt.links.new(mx.outputs['Result'],p.inputs['Base Color'])
bp=nt.nodes.new('ShaderNodeBump'); bp.name='OJ_bump'; bp.inputs['Strength'].default_value=0.35; nt.links.new(wv.outputs['Fac'],bp.inputs['Height']); nt.links.new(bp.outputs['Normal'],p.inputs['Normal'])
# ---- 4 lettering x1.12 in the facade plane (depth unchanged) ----
lo=bpy.data.objects[LET]; om=lo.data.copy(); om.name='OJ_lettering_orig_pre_oj'; om.use_fake_user=True
mw=lo.matrix_world; mi=mw.inverted(); ws=[mw@v.co for v in lo.data.vertices]
cc=sum(ws,Vector())/len(ws); SC=1.12
for v,w in zip(lo.data.vertices,ws):
    d=w-cc; a=d.dot(AL); o=d.dot(OUT); z=d.z
    v.co=mi@(cc+AL*a*SC+OUT*o+Vector((0,0,z*SC)))
lo.data.update()
ws=[mw@v.co for v in lo.data.vertices]; print('lettering z',round(min(w.z for w in ws),3),round(max(w.z for w in ws),3),'width',round(max((w-cen).dot(AL) for w in ws)-min((w-cen).dot(AL) for w in ws),3))
# ---- 5 block base: warmer, less regular split-face ----
for mn in BLK:
    m=bpy.data.materials[mn]; nt=m.node_tree; br=nt.nodes['Brick Texture']
    st['vals'][mn]={'Brick Texture|Color1':list(br.inputs['Color1'].default_value),'Brick Texture|Color2':list(br.inputs['Color2'].default_value),'Brick Texture|Mortar':list(br.inputs['Mortar'].default_value),'Brick Texture|Bias':br.inputs['Bias'].default_value}
    br.inputs['Color2'].default_value=(0.225,0.207,0.186,1); br.inputs['Mortar'].default_value=(0.30,0.29,0.27,1); br.inputs['Bias'].default_value=0.15
    vec_src=br.inputs['Vector'].links[0].from_socket
    n2=nt.nodes.new('ShaderNodeTexNoise'); n2.name='OJ_block_noise'; n2.inputs['Scale'].default_value=9.0; n2.inputs['Detail'].default_value=2.0
    nt.links.new(vec_src,n2.inputs['Vector'])
    r2=nt.nodes.new('ShaderNodeValToRGB'); r2.name='OJ_block_ramp'; r2.color_ramp.elements[0].color=(0.17,0.16,0.145,1); r2.color_ramp.elements[1].color=(0.36,0.33,0.29,1)
    nt.links.new(n2.outputs['Fac'],r2.inputs['Fac']); nt.links.new(r2.outputs['Color'],br.inputs['Color1'])
# ---- 6 entrance landing pad over the OSM path seams (sloped top, 2-5 cm proud, scored 1.25 m joints) ----
M_pad=mat('OJ_Schmitt_entrance_landing_concrete_UNVERIFIED',(0.5,0.49,0.46),0.8); nt=M_pad.node_tree; p=nt.nodes['Principled BSDF']
tc=nt.nodes.new('ShaderNodeTexCoord'); mp=nt.nodes.new('ShaderNodeMapping'); mp.inputs['Rotation'].default_value[2]=-math.atan2(AL.y,AL.x)
bt=nt.nodes.new('ShaderNodeTexBrick'); bt.offset=0.0; bt.inputs['Scale'].default_value=1.0; bt.inputs['Brick Width'].default_value=1.25; bt.inputs['Row Height'].default_value=1.25; bt.inputs['Mortar Size'].default_value=0.012
bt.inputs['Color1'].default_value=(0.52,0.505,0.475,1); bt.inputs['Color2'].default_value=(0.49,0.48,0.45,1); bt.inputs['Mortar'].default_value=(0.22,0.215,0.2,1)
nt.links.new(tc.outputs['Object'],mp.inputs['Vector']); nt.links.new(mp.outputs['Vector'],bt.inputs['Vector']); nt.links.new(bt.outputs['Color'],p.inputs['Base Color'])
def ztop(o): return 138.805 if o<=2.0 else 138.805-(o-2.0)/1.6*0.07
bm=bmesh.new(); box(bm,-2.5,2.5,0.70,3.60,138.60,138.80,zt=ztop); newobj('OJ_Schmitt_entrance_landing_pad_scored',bm,M_pad)
json.dump(st,open(SJ,'w'),indent=1); sc['oj_state']=json.dumps(st); print('OJ BUILT', len(col.objects))
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
