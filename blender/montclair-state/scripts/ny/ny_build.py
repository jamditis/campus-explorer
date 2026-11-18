# ny (Oct 31 2026 ~12:40 AM ET, MAIN): (1) the 12 NK north-classroom chairs (box seat + box back = dark slabs in the nx
# closeup) get moulded polypropylene shells (dished seat, waterfall front, curved reclined back that wraps at the sides),
# sitting on the existing NO legs; the NK seat/back boxes are hidden (render+viewport), not deleted, and restored on REVERT.
# (2) faint ghosting (erased-writing streaks) on the N classroom whiteboard as a 1 mm overlay plane; marker caps.
# (3) NY cameras. ALL UNVERIFIED (no photo of the N classroom).
import bpy, os, json, mathutils, bmesh, math
SAVE=os.environ.get('SAVE')=='1'; REVERT=os.environ.get('REVERT')=='1'
CN='NY_CCOM_N_classroom_shell_chairs_board_ghosting_20261031ny'; sc=bpy.context.scene
MATN=('NY_whiteboard_ghosting_UNVERIFIED','NY_clock_rim_black_UNVERIFIED','NY_clock_face_white_UNVERIFIED')
def nkchairs():
    out=[]
    for r in (0,1):
        for k in (0,1,2):
            for dx in (-0.45,0.45):
                b='NK N classroom chair r%d t%d %+.2f '%(r,k,dx); out.append((b+'seat',b+'back'))
    return out
def revert():
    c=bpy.data.collections.get(CN)
    if c:
        for o in list(c.objects):
            d=o.data; bpy.data.objects.remove(o)
            if d and d.users==0:
                if d.name in bpy.data.cameras: bpy.data.cameras.remove(d)
                elif d.name in bpy.data.meshes: bpy.data.meshes.remove(d)
        bpy.data.collections.remove(c)
    for mn in MATN:
        m=bpy.data.materials.get(mn)
        if m and m.users==0: bpy.data.materials.remove(m)
    if 'ny_state' in sc:
        st=json.loads(sc['ny_state'])
        for n,(hr,hv) in st.get('hidden',{}).items():
            o=bpy.data.objects.get(n)
            if o: o.hide_render=hr; o.hide_viewport=hv
    for k in ('ny_state','ny_note'):
        if k in sc: del sc[k]
    bpy.context.view_layer.update()
if REVERT:
    revert(); bpy.ops.wm.save_mainfile(); raise SystemExit
revert()
state={'hidden':{}}
col=bpy.data.collections.new(CN); sc.collection.children.link(col)
def tag(o,layer):
    o['msu_building']='School of Communication and Media'; o['msu_area']='ccom'; o['msu_layer']=layer
    o['msu_merge_role']='live'; o['msu_target_collection']='MSU_CCOM'; o['msu_tag_session']='ny'; o['msu_verified']='UNVERIFIED'
def link(nm,me,layer,shadow=True):
    o=bpy.data.objects.new(nm,me); col.objects.link(o); tag(o,layer); o.visible_shadow=shadow; return o
# ---- (1) moulded shells
def lerp(a,b,t): return a+(b-a)*t
PROF=[(0.228,-0.032),(0.222,-0.012),(0.208,0.004),(0.185,0.011),(0.14,0.013),(0.07,0.010),(0.0,0.007),(-0.07,0.009),(-0.125,0.016),
      (-0.165,0.032),(-0.192,0.062),(-0.207,0.105),(-0.215,0.16),(-0.222,0.23),(-0.23,0.30),(-0.238,0.37),(-0.246,0.43),(-0.252,0.475),(-0.262,0.505)]
def resample(P,n):
    L=[0]; 
    for i in range(1,len(P)): L.append(L[-1]+math.dist(P[i],P[i-1]))
    out=[]
    for s in range(n):
        t=L[-1]*s/(n-1); i=max(1,next(i for i in range(1,len(L)) if L[i]>=t-1e-9)); f=(t-L[i-1])/max(L[i]-L[i-1],1e-9)
        out.append((lerp(P[i-1][0],P[i][0],f),lerp(P[i-1][1],P[i][1],f)))
    return out
PR=resample(PROF,34); NX_=15; T=float(os.environ.get('SHELLT','0.011'))
def mid(i,j):
    u,z=PR[i]; s=-1+2*j/(NX_-1)
    wb=min(1,max(0,(z-0.05)/0.12)); wb=wb*wb*(3-2*wb)          # 0 on the seat, 1 on the back
    hw=lerp(0.222,0.212,wb)-(0.02*max(0,(u-0.17)/0.06) if wb==0 else 0)   # front corners pulled in a little
    x=s*hw
    z2=z+0.010*s*s*(1-wb)                                       # seat dish: sides rise 1 cm
    u2=u+0.045*s*s*wb                                           # back wraps forward at the sides
    if wb>0.9 and z>0.44: z2-=0.02*s**4                          # rounded top corners
    return mathutils.Vector((x,u2,z2))
def shell_mesh(nm):
    S=[[mid(i,j) for j in range(NX_)] for i in range(len(PR))]
    nI,nJ=len(PR),NX_; N=[[None]*nJ for _ in range(nI)]
    for i in range(nI):
        for j in range(nJ):
            du=S[min(i+1,nI-1)][j]-S[max(i-1,0)][j]; dv=S[i][min(j+1,nJ-1)]-S[i][max(j-1,0)]
            n=dv.cross(du).normalized()
            N[i][j]=n
    bm=bmesh.new()
    A=[[bm.verts.new(S[i][j]+N[i][j]*T/2) for j in range(nJ)] for i in range(nI)]
    B=[[bm.verts.new(S[i][j]-N[i][j]*T/2) for j in range(nJ)] for i in range(nI)]
    for i in range(nI-1):
        for j in range(nJ-1):
            bm.faces.new((A[i][j],A[i][j+1],A[i+1][j+1],A[i+1][j])); bm.faces.new((B[i][j],B[i+1][j],B[i+1][j+1],B[i][j+1]))
    for i in range(nI-1):
        bm.faces.new((A[i][0],A[i+1][0],B[i+1][0],B[i][0])); bm.faces.new((A[i][nJ-1],B[i][nJ-1],B[i+1][nJ-1],A[i+1][nJ-1]))
    for j in range(nJ-1):
        bm.faces.new((A[0][j],B[0][j],B[0][j+1],A[0][j+1])); bm.faces.new((A[nI-1][j],A[nI-1][j+1],B[nI-1][j+1],B[nI-1][j]))
    bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
    me=bpy.data.meshes.new(nm); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth=True
    return me
ZB=float(os.environ.get('ZB','138.095'))+T/2-0.007   # underside of the flat seat region ~5 mm below the NO leg tops (138.10)
n_sh=0
for sn,bn in nkchairs():
    so=bpy.data.objects.get(sn); bo=bpy.data.objects.get(bn)
    if not so or not bo: continue
    sc_=sum((so.matrix_world@v.co for v in so.data.vertices),mathutils.Vector())/8
    bc=sum((bo.matrix_world@v.co for v in bo.data.vertices),mathutils.Vector())/8
    fwd=mathutils.Vector((sc_.x-bc.x,sc_.y-bc.y,0)).normalized(); rt=mathutils.Vector((fwd.y,-fwd.x,0))
    M=mathutils.Matrix(((rt.x,fwd.x,0,sc_.x),(rt.y,fwd.y,0,sc_.y),(0,0,1,ZB),(0,0,0,1)))
    nm='NY N classroom moulded shell chair %s (UNVERIFIED)'%sn.replace('NK N classroom chair ','').replace(' seat','')
    o=link(nm,shell_mesh(nm),'furniture'); o.matrix_world=M
    o.data.materials.append(so.material_slots[0].material)
    for x in (so,bo):
        state['hidden'][x.name]=(x.hide_render,x.hide_viewport); x.hide_render=True; x.hide_viewport=True
    n_sh+=1
state['shells']=n_sh; print('NY shells',n_sh)
# ---- (2) whiteboard ghosting overlay (board face y 17.86, x 0.6..5.4, z 138.55..139.75) + marker caps
m=bpy.data.materials.new(MATN[0]); m.use_nodes=True; nt=m.node_tree; nd=nt.nodes; lk=nt.links
for x in list(nd): nd.remove(x)
outn=nd.new('ShaderNodeOutputMaterial'); mix=nd.new('ShaderNodeMixShader'); tr=nd.new('ShaderNodeBsdfTransparent')
df=nd.new('ShaderNodeBsdfPrincipled'); df.inputs['Base Color'].default_value=(0.55,0.56,0.6,1); df.inputs['Roughness'].default_value=0.6
tc=nd.new('ShaderNodeTexCoord'); mp=nd.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value=(1.0,9.0,1.0)
wv=nd.new('ShaderNodeTexNoise'); wv.inputs['Scale'].default_value=6.0; wv.inputs['Detail'].default_value=6.0
nz=nd.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value=2.2; nz.inputs['Detail'].default_value=3.0
mul=nd.new('ShaderNodeMath'); mul.operation='MULTIPLY'
cr=nd.new('ShaderNodeValToRGB'); cr.color_ramp.elements[0].position=0.30; cr.color_ramp.elements[1].position=0.62
cr.color_ramp.elements[1].color=(float(os.environ.get('GHOST','0.42')),)*3+(1,)
lk.new(tc.outputs['Object'],mp.inputs['Vector']); lk.new(mp.outputs['Vector'],wv.inputs['Vector']); lk.new(tc.outputs['Object'],nz.inputs['Vector'])
lk.new(wv.outputs['Fac'],mul.inputs[0]); lk.new(nz.outputs['Fac'],mul.inputs[1]); lk.new(mul.outputs[0],cr.inputs['Fac'])
lk.new(cr.outputs['Color'],mix.inputs['Fac']); lk.new(tr.outputs[0],mix.inputs[1]); lk.new(df.outputs[0],mix.inputs[2]); lk.new(mix.outputs[0],outn.inputs['Surface'])
m.blend_method='HASHED' if hasattr(m,'blend_method') else None
bm=bmesh.new(); vs=[bm.verts.new(v) for v in ((0.62,17.859,138.57),(5.38,17.859,138.57),(5.38,17.859,139.73),(0.62,17.859,139.73))]; bm.faces.new(vs)
me=bpy.data.meshes.new('NY whiteboard ghosting'); bm.to_mesh(me); bm.free(); me.materials.append(m)
g=link('NY N classroom whiteboard ghosting overlay (UNVERIFIED)',me,'furniture',shadow=False)
g.visible_glossy=True
YF=17.86; mz=138.55-0.022-0.004
for nm,x in (('black',2.1),('blue',2.32),('red',3.6)):
    mk_=bpy.data.objects.get('NX N classroom marker %s (UNVERIFIED)'%nm)
    if not mk_: continue
    bm=bmesh.new(); r=bmesh.ops.create_cone(bm,cap_ends=True,segments=12,radius1=0.0104,radius2=0.0104,depth=0.032)
    for v in r['verts']: v.co=mathutils.Vector((x+0.0505+v.co.z,YF-0.045+v.co.x,mz+0.009+v.co.y))
    addc=bmesh.ops.create_cube(bm,size=1.0)
    for v in addc['verts']: v.co=mathutils.Vector((x+0.047+v.co.x*0.022,YF-0.045+v.co.y*0.004,mz+0.0205+v.co.z*0.003))   # pocket clip
    me=bpy.data.meshes.new('NY marker cap '+nm); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth=True
    o=link('NY N classroom marker cap %s (UNVERIFIED)'%nm,me,'furniture'); o.data.materials.append(mk_.material_slots[0].material)
# ---- (2b) generic classroom wall clock above the whiteboard (wall face y 17.9), UNVERIFIED
def pm(n,c,r):
    m=bpy.data.materials.new(n); m.use_nodes=True; b=m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value=(*c,1); b.inputs['Roughness'].default_value=r; return m
CX,CZ=float(os.environ.get('CLKX','3.0')),float(os.environ.get('CLKZ','140.12')); YW=17.895
def disc(bm,r,y0,y1,seg=40):
    q=bmesh.ops.create_cone(bm,cap_ends=True,segments=seg,radius1=r,radius2=r,depth=y1-y0)
    for v in q['verts']: v.co=mathutils.Vector((CX+v.co.x,(y0+y1)/2+v.co.z,CZ+v.co.y))
bm=bmesh.new(); disc(bm,0.155,YW-0.045,YW)
def rbox(bm,cx,cz,w,h,y0,y1,ang):
    q=bmesh.ops.create_cube(bm,size=1.0); ca,sa=math.cos(ang),math.sin(ang)
    for v in q['verts']:
        lx,lz=v.co.x*w,v.co.z*h+h/2*0; v.co=mathutils.Vector((cx+lx*ca-lz*sa,(y0+y1)/2+v.co.y*(y1-y0),cz+lx*sa+lz*ca))
for k in range(12):
    a=k*math.pi/6; rbox(bm,CX+0.118*math.sin(a),CZ+0.118*math.cos(a),0.006 if k%3 else 0.010,0.022,YW-0.0485,YW-0.044,-a)
# hands at ~10:10 (centre offset so they start at the hub)
for L,a,w in ((0.075,-math.radians(300),0.008),(0.11,-math.radians(60),0.005)):
    rbox(bm,CX+L/2*math.sin(-a),CZ+L/2*math.cos(-a),w,L,YW-0.051,YW-0.0487,a)
mk_=bpy.data.meshes.new('NY classroom wall clock'); bm.to_mesh(mk_); bm.free(); mk_.materials.append(pm(MATN[1],(0.02,0.02,0.02),0.4))
link('NY N classroom wall clock rim, ticks and hands (UNVERIFIED)',mk_,'furniture')
bm=bmesh.new(); disc(bm,0.137,YW-0.047,YW-0.04)
mf=bpy.data.meshes.new('NY classroom wall clock face'); bm.to_mesh(mf); bm.free(); mf.materials.append(pm(MATN[2],(0.85,0.85,0.83),0.25))
link('NY N classroom wall clock face (UNVERIFIED)',mf,'furniture')
# ---- cameras
def cam(nm,loc,tgt,lens_):
    c=bpy.data.cameras.new(nm); c.lens=lens_; c.clip_start=0.05; o=bpy.data.objects.new(nm,c); o.location=loc
    o.rotation_euler=(mathutils.Vector(tgt)-mathutils.Vector(loc)).to_track_quat('-Z','Y').to_euler(); col.objects.link(o); tag(o,'camera')
def camcopy(nm,src):
    s=bpy.data.objects[src]; c=s.data.copy(); c.name=nm; o=bpy.data.objects.new(nm,c); o.matrix_world=s.matrix_world.copy(); col.objects.link(o); tag(o,'camera')
f=lambda k,d: tuple(float(x) for x in os.environ.get(k,d).split(','))
camcopy('NY_CAM_aerial_cutaway_oblique_CCOM_from_SW','NX_CAM_aerial_cutaway_oblique_CCOM_from_SW')
camcopy('NY_CAM_eye_atrium_looking_west_to_doors','NX_CAM_eye_atrium_looking_west_to_doors')
camcopy('NY_CAM_eye_1F_open_floor_cafe_looking_east','NX_CAM_eye_1F_open_floor_cafe_looking_east')
cam('NY_CAM_closeup_N_classroom_shell_chairs_clock_whiteboard',f('CLLOC','6.45,14.5,138.9'),f('CLTGT','1.5,17.0,138.42'),float(os.environ.get('CLLENS','24')))
sc['ny_state']=json.dumps(state)
sc['ny_note']='ny: N classroom moulded shell chairs (NK boxes hidden), whiteboard ghosting overlay + marker caps; NY cameras; UNVERIFIED'
print('NY objects',len(col.objects),'total',len(bpy.data.objects),{k:v for k,v in state.items() if k!='hidden'},'hidden',len(state['hidden']))
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
