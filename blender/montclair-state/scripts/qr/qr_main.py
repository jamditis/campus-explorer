# qr (Nov 2 2026 ~8:25 PM ET, MAIN, day 7 Richardson Hall). ALL UNVERIFIED, reversible: REVERT=1 -> pre-qr state.
# (1) Richardson 4 corner towers + penthouse: off-white precast panel cladding (1970s archive slides show white windowless
#     towers; current finish UNVERIFIED): UV-driven panel joints (2.4 m x 1.52 m), joint bump, vertical run-off streaks,
#     base grime, darker band under the cap. Cap sides -> dark bronze metal coping; cap/penthouse tops -> roof membrane.
#     New: coping lip rings, one louvred vent per outward tower face near the top + 2 per long penthouse face (guessed).
# (2) Roof units: galvanised metal with panel seams, curbs, fan disc + guard ring on each top (generic RTU, UNVERIFIED).
# (3) Ground_ortho_grass: QR_ tone mask (world box round Richardson S/SW/E, only where the ortho is pale) -> lawn tone.
# (4) Camera QR_CAM_eye_richardson_NE_door (checks the qq NE door).
import bpy, bmesh, os, json, math
from mathutils import Vector
REV=os.environ.get('REVERT')=='1'
TW='QP_Richardson_white_corner_towers_UNVERIFIED'; PH='QP_Richardson_roof_penthouse_units_UNVERIFIED'
COL='QR_Richardson_tower_detail_UNVERIFIED'; J='data/qr/added.json'
MEMB='QP_Richardson_roof_membrane'; GMAT='Ground_ortho_grass'
def revert():
    d=json.load(open(J)) if os.path.exists(J) else {}
    for n,prev in d.get('faces',{}).items():
        me=bpy.data.meshes[n]
        miss=[mn for mn in prev['slots'] if mn not in bpy.data.materials]
        if miss:
            with bpy.data.libraries.load('montclair_state_pre_20261102qr.blend',link=False) as (src,dst): dst.materials=miss
            print('QR restored materials from backup',miss)
        while len(me.materials)>prev['nslots']: me.materials.pop()
        for i,mn in enumerate(prev['slots']): me.materials[i]=bpy.data.materials[mn]
        for f,mi in zip(me.polygons,prev['mi']): f.material_index=mi
        for mn in prev['slots']:
            m_=bpy.data.materials[mn]
            if m_.get('qr_fake'): m_.use_fake_user=False; del m_['qr_fake']
    c=bpy.data.collections.get(COL)
    if c:
        for o in list(c.objects): bpy.data.objects.remove(o,do_unlink=True)
        bpy.data.collections.remove(c)
    for k in ('meshes','materials','cameras'):
        for n in d.get(k,[]):
            x=getattr(bpy.data,k).get(n)
            if x and x.users==0: getattr(bpy.data,k).remove(x)
    nt=bpy.data.materials[GMAT].node_tree
    for nd in [n for n in nt.nodes if n.name.startswith('QR_')]: nt.nodes.remove(nd)
    pb=nt.nodes['Principled BSDF']
    if not pb.inputs['Base Color'].is_linked: nt.links.new(nt.nodes['QO_tone_mix'].outputs[2],pb.inputs['Base Color'])
    gt_=bpy.data.materials['cd_grass'].node_tree
    for nd in [n for n in gt_.nodes if n.name.startswith('QR_')]: gt_.nodes.remove(nd)
    for tn,ts in (('Principled BSDF','Base Color'),('Translucent BSDF','Color')):
        if not gt_.nodes[tn].inputs[ts].is_linked: gt_.links.new(gt_.nodes['Mix'].outputs['Result'],gt_.nodes[tn].inputs[ts])
    print('QR reverted')
if REV or bpy.data.collections.get(COL): revert()
if REV:
    exec(open('scripts/pn/pn_sig.py').read())
    if os.environ.get('QRSAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')
    raise SystemExit
before={k:set(x.name for x in getattr(bpy.data,k)) for k in ('meshes','materials','cameras')}
rec={'faces':{}}
for n in (TW,PH):
    me=bpy.data.objects[n].data
    for m_ in me.materials:
        if not m_.use_fake_user: m_.use_fake_user=True; m_['qr_fake']=1
    rec['faces'][me.name]={'nslots':len(me.materials),'slots':[m.name for m in me.materials],'mi':[f.material_index for f in me.polygons]}
# ---------- materials
def newmat(name):
    m=bpy.data.materials.new(name); m.use_nodes=True; return m,m.node_tree.nodes,m.node_tree.links,m.node_tree.nodes['Principled BSDF']
def nd(N,t,**kw):
    n=N.new(t)
    for k,v in kw.items(): setattr(n,k,v)
    return n
def math_(N,L,op,a,b=None,cl=False):
    n=N.new('ShaderNodeMath'); n.operation=op; n.use_clamp=cl
    (L.new(a,n.inputs[0]) if not isinstance(a,(int,float)) else n.inputs[0].__setattr__('default_value',a))
    if b is not None: (L.new(b,n.inputs[1]) if not isinstance(b,(int,float)) else n.inputs[1].__setattr__('default_value',b))
    return n.outputs[0]
def joints(N,L,coord,period,half):
    s=math_(N,L,'DIVIDE',coord,period); f=math_(N,L,'FRACT',s); g=math_(N,L,'SUBTRACT',1.0,f); m=math_(N,L,'MINIMUM',f,g)
    m=math_(N,L,'MULTIPLY',m,period); return math_(N,L,'LESS_THAN',m,half)
pm,N,L,b=newmat('QR_Richardson_tower_precast_UNVERIFIED')
uv=N.new('ShaderNodeUVMap'); uv.uv_map='UVMap'; sp=N.new('ShaderNodeSeparateXYZ'); L.new(uv.outputs[0],sp.inputs[0])
ju=joints(N,L,sp.outputs[0],2.4,0.012); jz=joints(N,L,sp.outputs[1],1.52,0.012); jj=math_(N,L,'MAXIMUM',ju,jz)
# vertical streaks: noise stretched in z
cx=N.new('ShaderNodeCombineXYZ'); L.new(math_(N,L,'MULTIPLY',sp.outputs[0],1.6),cx.inputs[0]); L.new(math_(N,L,'MULTIPLY',sp.outputs[1],0.08),cx.inputs[1])
nz=N.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value=1.0; nz.inputs['Detail'].default_value=4; L.new(cx.outputs[0],nz.inputs['Vector'])
st=N.new('ShaderNodeMapRange'); st.inputs['From Min'].default_value=0.45; st.inputs['From Max'].default_value=0.68; st.inputs['To Min'].default_value=1.0; st.inputs['To Max'].default_value=0.74; L.new(nz.outputs['Fac'],st.inputs['Value'])
# per-panel tone variation
pu=math_(N,L,'FLOOR',math_(N,L,'DIVIDE',sp.outputs[0],2.4)); pz=math_(N,L,'FLOOR',math_(N,L,'DIVIDE',sp.outputs[1],1.52))
cp=N.new('ShaderNodeCombineXYZ'); L.new(pu,cp.inputs[0]); L.new(pz,cp.inputs[1])
wn=N.new('ShaderNodeTexWhiteNoise'); wn.noise_dimensions='3D'; L.new(cp.outputs[0],wn.inputs['Vector'])
pv=N.new('ShaderNodeMapRange'); pv.inputs['To Min'].default_value=0.94; pv.inputs['To Max'].default_value=1.03; L.new(wn.outputs['Value'],pv.inputs['Value'])
# base grime (z 136.6..138.6) and under-cap band (156.3..157)
gb=N.new('ShaderNodeMapRange'); gb.inputs['From Min'].default_value=136.6; gb.inputs['From Max'].default_value=138.8; gb.inputs['To Min'].default_value=0.72; gb.inputs['To Max'].default_value=1.0; L.new(sp.outputs[1],gb.inputs['Value'])
gt=N.new('ShaderNodeMapRange'); gt.inputs['From Min'].default_value=156.95; gt.inputs['From Max'].default_value=156.2; gt.inputs['To Min'].default_value=0.80; gt.inputs['To Max'].default_value=1.0; L.new(sp.outputs[1],gt.inputs['Value'])
jd=N.new('ShaderNodeMapRange'); jd.inputs['To Min'].default_value=1.0; jd.inputs['To Max'].default_value=0.55; L.new(jj,jd.inputs['Value'])
v=st.outputs[0]
for o in (pv.outputs[0],gb.outputs[0],gt.outputs[0],jd.outputs[0]): v=math_(N,L,'MULTIPLY',v,o)
mc=N.new('ShaderNodeMix'); mc.data_type='RGBA'; mc.blend_type='MULTIPLY'; mc.inputs[0].default_value=1.0
mc.inputs[6].default_value=(0.60,0.585,0.545,1)
cv=N.new('ShaderNodeCombineColor'); L.new(v,cv.inputs[0]); L.new(v,cv.inputs[1]); L.new(v,cv.inputs[2]); L.new(cv.outputs[0],mc.inputs[7])
L.new(mc.outputs[2],b.inputs['Base Color']); b.inputs['Roughness'].default_value=0.82
bp=N.new('ShaderNodeBump'); bp.inputs['Strength'].default_value=0.35; bp.inputs['Distance'].default_value=0.01; L.new(math_(N,L,'SUBTRACT',1.0,jj),bp.inputs['Height']); L.new(bp.outputs[0],b.inputs['Normal'])
cm,N,L,b=newmat('QR_Richardson_coping_bronze_UNVERIFIED'); b.inputs['Base Color'].default_value=(0.16,0.13,0.10,1); b.inputs['Metallic'].default_value=0.7; b.inputs['Roughness'].default_value=0.42
vm,N,L,b=newmat('QR_Richardson_louvre_dark_UNVERIFIED'); b.inputs['Base Color'].default_value=(0.11,0.105,0.10,1); b.inputs['Metallic'].default_value=0.5; b.inputs['Roughness'].default_value=0.5
km,N,L,b=newmat('QR_Richardson_fan_dark_UNVERIFIED'); b.inputs['Base Color'].default_value=(0.03,0.03,0.032,1); b.inputs['Roughness'].default_value=0.6
gm,N,L,b=newmat('QR_Richardson_rtu_galv_UNVERIFIED')
gp=N.new('ShaderNodeNewGeometry'); gs=N.new('ShaderNodeSeparateXYZ'); L.new(gp.outputs['Position'],gs.inputs[0])
A=Vector((math.cos(math.radians(-23.7)),math.sin(math.radians(-23.7)),0)); B=Vector((-A.y,A.x,0))
da=N.new('ShaderNodeVectorMath'); da.operation='DOT_PRODUCT'; da.inputs[1].default_value=A; L.new(gp.outputs['Position'],da.inputs[0])
db=N.new('ShaderNodeVectorMath'); db.operation='DOT_PRODUCT'; db.inputs[1].default_value=B; L.new(gp.outputs['Position'],db.inputs[0])
s1=joints(N,L,da.outputs['Value'],0.85,0.008); s2=joints(N,L,db.outputs['Value'],0.85,0.008); ss=math_(N,L,'MAXIMUM',s1,s2)
n2=N.new('ShaderNodeTexNoise'); n2.inputs['Scale'].default_value=2.5; L.new(gp.outputs['Position'],n2.inputs['Vector'])
r2=N.new('ShaderNodeMapRange'); r2.inputs['To Min'].default_value=0.85; r2.inputs['To Max'].default_value=1.05; L.new(n2.outputs['Fac'],r2.inputs['Value'])
sd=N.new('ShaderNodeMapRange'); sd.inputs['To Min'].default_value=1.0; sd.inputs['To Max'].default_value=0.45; L.new(ss,sd.inputs['Value'])
gv=math_(N,L,'MULTIPLY',r2.outputs[0],sd.outputs[0]); gc=N.new('ShaderNodeCombineColor'); [L.new(gv,gc.inputs[i]) for i in range(3)]
gx=N.new('ShaderNodeMix'); gx.data_type='RGBA'; gx.blend_type='MULTIPLY'; gx.inputs[0].default_value=1.0; gx.inputs[6].default_value=(0.42,0.43,0.43,1); L.new(gc.outputs[0],gx.inputs[7])
L.new(gx.outputs[2],b.inputs['Base Color']); b.inputs['Metallic'].default_value=0.75; b.inputs['Roughness'].default_value=0.48
memb=bpy.data.materials[MEMB]
# ---------- reassign tower/penthouse faces
def assign(me,slotmap):
    for i,m in enumerate(me.materials):
        if m.name in slotmap: me.materials[i]=slotmap[m.name]
tme=bpy.data.objects[TW].data; tme.materials[0]=pm; tme.materials.append(cm); tme.materials.append(memb)
for f in tme.polygons:
    zs=[tme.vertices[i].co.z for i in f.vertices]
    if f.normal.z>0.9: f.material_index=2
    elif min(zs)>=156.99: f.material_index=1
pme=bpy.data.objects[PH].data; pme.materials[0]=pm; pme.materials[1]=gm; pme.materials.append(memb)
for f in pme.polygons:
    zs=[pme.vertices[i].co.z for i in f.vertices]
    if f.normal.z>0.9 and abs(max(zs)-156.47)<0.01: f.material_index=2
# ---------- new geometry
col=bpy.data.collections.new(COL); bpy.context.scene.collection.children.link(col)
def newobj(name,mats):
    me=bpy.data.meshes.new(name); o=bpy.data.objects.new(name,me); col.objects.link(o)
    for m in mats: me.materials.append(m)
    o['UNVERIFIED_qr']='qr: Richardson tower/penthouse/RTU detail, generic (1971-75 slides show white windowless towers)'; return o,bmesh.new()
def quad(bm,pts,mi,want):
    f=bm.faces.new([bm.verts.new(p) for p in pts]); f.material_index=mi; f.normal_update()
    if f.normal.dot(want)<0: f.normal_flip()
def obox(bm,c,ax,ay,hx,hy,z0,z1,mi,bottom=False):
    cs=[c+ax*sx*hx+ay*sy*hy for sx,sy in ((-1,-1),(1,-1),(1,1),(-1,1))]
    for i in range(4):
        a,b_=cs[i],cs[(i+1)%4]; o=(a+b_)/2-c; o.z=0
        quad(bm,[Vector((a.x,a.y,z0)),Vector((b_.x,b_.y,z0)),Vector((b_.x,b_.y,z1)),Vector((a.x,a.y,z1))],mi,o)
    quad(bm,[Vector((p.x,p.y,z1)) for p in cs],mi,Vector((0,0,1)))
    if bottom: quad(bm,[Vector((p.x,p.y,z0)) for p in cs],mi,Vector((0,0,-1)))
def finish(o,bm):
    bmesh.ops.remove_doubles(bm,verts=bm.verts,dist=0.0005); bm.to_mesh(o.data); bm.free()
    for p in o.data.polygons: p.use_smooth=False
MW=bpy.data.objects[TW].matrix_world; CTR=Vector((84,264,0))
# tower boxes: recover from the side faces (z 136.6..157)
def boxes(me,ztop):
    out=[]; seen=set()
    sides=[f for f in me.polygons if abs(f.normal.z)<0.1 and abs(max(me.vertices[i].co.z for i in f.vertices)-ztop)<0.01]
    tops=[f for f in me.polygons if f.normal.z>0.9 and abs(me.vertices[f.vertices[0]].co.z-ztop)<0.01]
    return sides,tops
o,bm=newobj('QR_Richardson_tower_coping_lips_UNVERIFIED',[cm])
o2,bm2=newobj('QR_Richardson_tower_louvres_UNVERIFIED',[vm,cm])
def ring(bm,corners,ctr,z0,z1,w):
    inn=[]
    for i,c in enumerate(corners):
        a=corners[i-1]; b_=corners[(i+1)%len(corners)]
        d=(a-c).normalized()+(b_-c).normalized(); inn.append(c+d*w)  # inset ~w along both edges
    out=[c+(c-ctr).normalized()*0.02 for c in corners]
    n=len(corners)
    for i in range(n):
        j=(i+1)%n; P=lambda v,z:Vector((v.x,v.y,z))
        quad(bm,[P(out[i],z1),P(out[j],z1),P(inn[j],z1),P(inn[i],z1)],0,Vector((0,0,1)))
        quad(bm,[P(out[i],z0),P(out[j],z0),P(out[j],z1),P(out[i],z1)],0,((out[i]+out[j])/2-ctr))
        quad(bm,[P(inn[i],z0+0.01),P(inn[j],z0+0.01),P(inn[j],z1),P(inn[i],z1)],0,(ctr-(inn[i]+inn[j])/2))
def louvre(bm,a,b_,n,zc,w,h):
    t=(b_-a).normalized(); m=(a+b_)/2; nn=Vector((n.x,n.y,0)).normalized()
    c=m+nn*0.03; c.z=0
    # frame (closed box 6 cm deep, 4 cm proud) + slats
    obox(bm,c+nn*0.0,t,nn,w/2+0.06,0.035,zc-h/2-0.06,zc+h/2+0.06,1)
    k=int(h/0.16)
    for i in range(k):
        z=zc-h/2+0.08+i*(h-0.1)/max(k-1,1)
        obox(bm,c+nn*0.045,t,nn,w/2,0.03,z-0.035,z+0.02,0,bottom=True)
tsides,ttops=boxes(tme,157.2)
nl=0
for f in ttops:
    cs=[MW@tme.vertices[i].co for i in f.vertices]; ctr=sum(cs,Vector())/len(cs)
    ring(bm,cs,ctr,157.17,157.26,0.30)
# tower main faces (z top 157.0)
s157,t157=boxes(tme,157.0)
for f in s157:
    cs=[MW@tme.vertices[i].co for i in f.vertices]; zs=[c.z for c in cs]
    if min(zs)>140: continue
    bot=[c for c in cs if c.z<140]; a,b_=bot[0],bot[1]; m=(a+b_)/2; m.z=0; n=MW.to_3x3()@f.normal
    if n.dot((m-CTR).normalized())<0.35: continue   # outward faces only
    if (a-b_).length<3.0: continue
    louvre(bm2,Vector((a.x,a.y,0)),Vector((b_.x,b_.y,0)),n,155.3,1.5,1.1); nl+=1
# penthouse: louvres on the two long faces + coping ring
PW=bpy.data.objects[PH].matrix_world
ps,pt=boxes(pme,156.47)
for f in pt:
    cs=[PW@pme.vertices[i].co for i in f.vertices]; ring(bm,cs,sum(cs,Vector())/4,156.44,156.53,0.25)
for f in ps:
    cs=[PW@pme.vertices[i].co for i in f.vertices]; bot=sorted(cs,key=lambda c:c.z)[:2]; a,b_=bot; L_=(a-b_).length
    if L_<9: continue
    n=PW.to_3x3()@f.normal; t=(b_-a).normalized()
    for s in (-0.25,0.25):
        p=(a+b_)/2+t*L_*s; louvre(bm2,Vector((p.x,p.y,0))-t*1.2,Vector((p.x,p.y,0))+t*1.2,n,154.6,2.2,1.4); nl+=1
finish(o,bm); finish(o2,bm2)
# RTUs: curbs + fan disc + guard ring
o3,bm3=newobj('QR_Richardson_rtu_fans_curbs_UNVERIFIED',[km,gm,vm])
Av=Vector((A.x,A.y,0)); Bv=Vector((B.x,B.y,0)); ZR=151.5
for (x,y,z) in ((89.5,259,153.4),(78.5,263.5,154.6),(71.5,268,153.1),(84,249.5,153.9)):
    c=Vector((x,y,0))
    obox(bm3,c,Av,Bv,1.40,1.70,ZR-0.04,ZR+0.18,2)                     # curb (unit sits on it, 10 cm wider)
    r=bmesh.ops.create_circle(bm3,cap_ends=True,segments=20,radius=0.45)
    for vv in r['verts']: vv.co+=Vector((x+Bv.x*0.6,y+Bv.y*0.6,z+0.015))
    for ff in {f for vv in r['verts'] for f in vv.link_faces}: ff.material_index=0
    rr=bmesh.ops.create_cone(bm3,cap_ends=False,segments=20,radius1=0.5,radius2=0.5,depth=0.18)
    for vv in rr['verts']: vv.co+=Vector((x+Bv.x*0.6,y+Bv.y*0.6,z+0.09))
    for ff in {f for vv in rr['verts'] for f in vv.link_faces}: ff.material_index=1
    obox(bm3,c-Bv*0.7,Av,Bv,1.1,0.25,z-0.9,z-0.35,2)                  # side intake louvre panel
finish(o3,bm3)
# ---------- grass tone mask (Ground_ortho_grass), world box round Richardson, pale-only
nt=bpy.data.materials[GMAT].node_tree; N=nt.nodes; L=nt.links; pb=N['Principled BSDF']
prev=pb.inputs['Base Color'].links[0].from_socket
geo=N.new('ShaderNodeNewGeometry'); geo.name='QR_geo'; sp=N.new('ShaderNodeSeparateXYZ'); sp.name='QR_sep'; L.new(geo.outputs['Position'],sp.inputs[0])
X0,X1,Y0,Y1,F=float(os.environ.get('GX0','45')),float(os.environ.get('GX1','140')),float(os.environ.get('GY0','218')),float(os.environ.get('GY1','305')),5.0
def edge(ax,lo,hi):
    a=N.new('ShaderNodeMapRange'); a.name='QR_mra'+ax; a.interpolation_type='SMOOTHSTEP'; a.inputs['From Min'].default_value=lo; a.inputs['From Max'].default_value=lo+F; L.new(sp.outputs[ax],a.inputs['Value'])
    b_=N.new('ShaderNodeMapRange'); b_.name='QR_mrb'+ax; b_.interpolation_type='SMOOTHSTEP'; b_.inputs['From Min'].default_value=hi; b_.inputs['From Max'].default_value=hi-F; L.new(sp.outputs[ax],b_.inputs['Value'])
    m=N.new('ShaderNodeMath'); m.name='QR_m'+ax; m.operation='MULTIPLY'; L.new(a.outputs[0],m.inputs[0]); L.new(b_.outputs[0],m.inputs[1]); return m
mx=edge('X',X0,X1); my=edge('Y',Y0,Y1)
bw=N.new('ShaderNodeRGBToBW'); bw.name='QR_lum'; L.new(prev,bw.inputs[0])
pl=N.new('ShaderNodeMapRange'); pl.name='QR_pale'; pl.inputs['From Min'].default_value=float(os.environ.get('PL0','0.16')); pl.inputs['From Max'].default_value=float(os.environ.get('PL1','0.32')); L.new(bw.outputs[0],pl.inputs['Value'])
f1=N.new('ShaderNodeMath'); f1.name='QR_f1'; f1.operation='MULTIPLY'; L.new(mx.outputs[0],f1.inputs[0]); L.new(my.outputs[0],f1.inputs[1])
f2=N.new('ShaderNodeMath'); f2.name='QR_f2'; f2.operation='MULTIPLY'; L.new(f1.outputs[0],f2.inputs[0]); L.new(pl.outputs[0],f2.inputs[1])
f3=N.new('ShaderNodeMath'); f3.name='QR_f3'; f3.operation='MULTIPLY'; f3.inputs[1].default_value=float(os.environ.get('STR','0.9')); L.new(f2.outputs[0],f3.inputs[0])
grass=N['Image Texture']; hsv=N.new('ShaderNodeHueSaturation'); hsv.name='QR_hsv'; L.new(grass.outputs['Color'],hsv.inputs['Color']); hsv.inputs['Saturation'].default_value=0.9; hsv.inputs['Value'].default_value=float(os.environ.get('VAL','0.72'))
tint=N.new('ShaderNodeMix'); tint.name='QR_tint'; tint.data_type='RGBA'; tint.blend_type='MULTIPLY'; tint.inputs[0].default_value=1.0; L.new(prev,tint.inputs[6]); tint.inputs[7].default_value=(0.50,0.64,0.38,1)
lawn=N.new('ShaderNodeMix'); lawn.name='QR_lawn'; lawn.data_type='RGBA'; lawn.inputs[0].default_value=0.3; L.new(hsv.outputs[0],lawn.inputs[6]); L.new(tint.outputs[2],lawn.inputs[7])
out=N.new('ShaderNodeMix'); out.name='QR_tone_mix'; out.data_type='RGBA'; L.new(f3.outputs[0],out.inputs[0]); L.new(prev,out.inputs[6]); L.new(lawn.outputs[2],out.inputs[7]); L.new(out.outputs[2],pb.inputs['Base Color'])
# ---------- cd_grass clumps: same world box -> greener, darker (pale dry tips round Richardson)
gm_=bpy.data.materials['cd_grass']; gt_=gm_.node_tree; GN_=gt_.nodes; GL_=gt_.links
fs=GN_['Mix'].outputs['Result']
if True:
    g2=GN_.new('ShaderNodeNewGeometry'); g2.name='QR_g2'; s2=GN_.new('ShaderNodeSeparateXYZ'); s2.name='QR_s2'; GL_.new(g2.outputs['Position'],s2.inputs[0])
    acc=None
    for ax,lo,hi in (('X',X0,X1),('Y',Y0,Y1)):
        a=GN_.new('ShaderNodeMapRange'); a.name='QR_ga'+ax; a.interpolation_type='SMOOTHSTEP'; a.inputs['From Min'].default_value=lo; a.inputs['From Max'].default_value=lo+F; GL_.new(s2.outputs[ax],a.inputs['Value'])
        b2=GN_.new('ShaderNodeMapRange'); b2.name='QR_gb'+ax; b2.interpolation_type='SMOOTHSTEP'; b2.inputs['From Min'].default_value=hi; b2.inputs['From Max'].default_value=hi-F; GL_.new(s2.outputs[ax],b2.inputs['Value'])
        m=GN_.new('ShaderNodeMath'); m.name='QR_gm'+ax; m.operation='MULTIPLY'; GL_.new(a.outputs[0],m.inputs[0]); GL_.new(b2.outputs[0],m.inputs[1])
        if acc is None: acc=m
        else:
            m2=GN_.new('ShaderNodeMath'); m2.name='QR_gmxy'; m2.operation='MULTIPLY'; GL_.new(acc.outputs[0],m2.inputs[0]); GL_.new(m.outputs[0],m2.inputs[1]); acc=m2
    mx2=GN_.new('ShaderNodeMix'); mx2.name='QR_grass_tone'; mx2.data_type='RGBA'; mx2.blend_type='MULTIPLY'; GL_.new(acc.outputs[0],mx2.inputs[0])
    GL_.new(fs,mx2.inputs[6]); mx2.inputs[7].default_value=(float(os.environ.get('GR','0.62')),float(os.environ.get('GG','0.78')),float(os.environ.get('GB','0.45')),1); GL_.new(mx2.outputs[2],GN_['Principled BSDF'].inputs['Base Color']); GL_.new(mx2.outputs[2],GN_['Translucent BSDF'].inputs['Color'])
    print('QR cd_grass tone on')
# ---------- NE door camera
dg=bpy.context.evaluated_depsgraph_get(); T=bpy.data.objects['Terrain_LiDAR_DTM_1m']; Te=T.evaluated_get(dg); Mi=T.matrix_world.inverted()
def gz(x,y):
    ok,loc,nr,ix=Te.ray_cast(Mi@Vector((x,y,400)),Mi.to_3x3()@Vector((0,0,-1)),depsgraph=dg); return (T.matrix_world@loc).z if ok else 137.8
door=Vector((79.95,290.37,0)); dv=(door-CTR).normalized(); cl=door+dv*11+Vector((dv.y,-dv.x,0))*9
cd=bpy.data.cameras.new('QR_CAM_eye_richardson_NE_door'); cd.lens=24; cd.clip_end=3000; co=bpy.data.objects.new('QR_CAM_eye_richardson_NE_door',cd); col.objects.link(co)
co.location=Vector((cl.x,cl.y,gz(cl.x,cl.y)+1.65)); tg=Vector((door.x,door.y,gz(door.x,door.y)+2.6)); co.rotation_euler=(tg-co.location).to_track_quat('-Z','Y').to_euler()
cd=bpy.data.cameras.new('QR_CAM_closeup_richardson_S_tower_cladding'); cd.lens=30; cd.clip_end=3000; c2=bpy.data.objects.new('QR_CAM_closeup_richardson_S_tower_cladding',cd); col.objects.link(c2)
c2.location=Vector((104.0,218.0,gz(104.0,218.0)+1.65)); c2.rotation_euler=(Vector((93.6,235.0,150.5))-c2.location).to_track_quat('-Z','Y').to_euler()
print('QR cam',[round(c,2) for c in co.location],'louvres',nl)
for k in ('meshes','materials','cameras'): rec[k]=sorted(set(x.name for x in getattr(bpy.data,k))-before[k])
json.dump(rec,open(J,'w'))
exec(open('scripts/pn/pn_sig.py').read())
if os.environ.get('QRSAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')
