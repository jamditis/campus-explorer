# ws105: W bank of College Ave S leg (W of the WS103 walk, E face of Chapin Hall) built in layers per prep/ws104_W_bank_Chapin_terrace:
# lower concrete walkway (LiDAR flat ~122.2-122.3) -> planted mulch bed + white retaining walls where LiDAR shows vertical faces
# (s 5.5-13.5, 18.5-26.5, low taper 26.5-30.5) -> 3 stairs (walk -> walkway) with cheek walls + steel rails -> shrubs -> terrain re-seat.
import bpy,bmesh,numpy as np,sys,os,json,random
from mathutils import Vector
sys.path.insert(0,'/workspace/nj-scenes/montclair-state/scripts/ws105'); from frame105 import *
OUT='/workspace/nj-scenes/montclair-state/scripts/ws105/'
def sm(a,b,x): t=np.clip((x-a)/(b-a),0,1); return t*t*(3-2*t)
L=np.load('/workspace/nj-scenes/montclair-state/scripts/ws102/lid_so.npz'); LS,LO,LZ=L['s'],L['o'],L['z']
def lid(s,o,rs=0.6,ro=0.45):
    m=(np.abs(LS-s)<rs)&(np.abs(LO-o)<ro); return float(np.median(LZ[m])) if m.sum()>=2 else None
def getW(ob):
    me=ob.data; n=len(me.vertices); c=np.empty(n*3); me.vertices.foreach_get('co',c); c=c.reshape(-1,3)
    M=np.array(ob.matrix_world); return c@M[:3,:3].T+M[:3,3], M
O=bpy.data.objects
for o in [o for o in O if o.name.startswith('WS105_')]: O.remove(o)
# ---- walk W edge from the WS103 mesh (top verts only)
walk=[o for o in O if o.name.startswith('WS103_CollegeAve_S_W_sidewalk')][0]; WW,_=getW(walk)
SO=np.array([so(q) for q in WW]); top={}
for (s,o),z in zip(SO,WW[:,2]):
    k=round(s*2)/2; 
    if k not in top or o>top[k][0]+0.02 or (abs(o-top[k][0])<0.02 and z>top[k][1]): top[k]=(o,z)
ks=np.array(sorted(top)); OE=np.array([top[k][0] for k in ks]); ZE=np.array([top[k][1] for k in ks])
def oE(s): return float(np.interp(s,ks,OE))
def zE(s): return float(np.interp(s,ks,ZE))
print('B105 walk edge s',ks.min(),ks.max(),'o',OE.min(),OE.max())
# ---- lower walkway level
sr=np.arange(-2,43,1.0); zl=[]
for s in sr:
    o0=12.5 if s<5 else 10.5
    m=(np.abs(LS-s)<1.5)&(LO>o0)&(LO<14.5); zl.append(np.median(LZ[m]) if m.sum()>3 else np.nan)
zl=np.array(zl); ok=np.isfinite(zl); zl=np.interp(sr,sr[ok],zl[ok]); zl=np.convolve(np.pad(zl,3,mode='edge'),np.ones(7)/7,'valid')
def zlow(s): return float(np.interp(s,sr,zl))+0.02
# ---- wall line / bed end (o) and wall weight
OWk=([-1,3,5.5,13.5,14.5,17.5,18.5,26.5,30.5,32,42],[11.8,11.0,9.2,8.4,9.8,9.8,8.3,8.6,9.0,9.6,9.4])
def ow(s): return float(np.interp(s,*OWk))
WALLS=[(5.5,13.5,1.0),(18.5,26.5,1.0),(26.5,30.5,0.6)]
def wg(s):
    w=0.0
    for a,b,h in WALLS: w=max(w,h*sm(a-0.01,a+0.6,s)*(1-sm(b-0.6,b+0.01,s)))
    return w
WS0,WS1=0.0,41.0; OB=13.9
# bed end height at wall from LiDAR just inside the wall
srb=np.arange(WS0,WS1+0.01,0.5); zbr=[]
for s in srb:
    v=lid(s,ow(s)-0.6); zbr.append(v if v is not None else np.nan)
zbr=np.array(zbr); ok=np.isfinite(zbr); zbr=np.interp(srb,srb[ok],zbr[ok]); zbr=np.convolve(np.pad(zbr,2,mode='edge'),np.ones(5)/5,'valid')
def zbend(s):
    zt=zE(s)-0.05; zlo=zlow(s)+0.03; zb=min(max(float(np.interp(s,srb,zbr)),zlo),zt-0.05)
    return zlo+wg(s)*(zb-zlo)
def bedz(s,o):
    o1=oE(s); oe=ow(s)+0.3*(1-min(wg(s)*3,1)); t=np.clip((o-o1)/max(oe-o1,0.1),0,1)
    zt=zE(s)-0.05; ze=zbend(s); t2=t**1.3 if wg(s)>0.3 else t*t*(3-2*t)
    return zt+(ze-zt)*t2
# ---- stairs
STAIRS=[]
for c in (9.5,21.0,28.0):
    zt=zE(c); zb=zlow(c); n=max(3,int(round((zt-zb)/0.16))); r=(zt-zb)/n; o1=oE(c)
    STAIRS.append(dict(c=c,n=n,r=r,o1=o1,zt=zt,zb=zb,end=o1+(n-1)*0.30))
HW=0.9; CW=0.2
def instair(s):
    for st in STAIRS:
        if abs(s-st['c'])<HW+CW+0.02: return st
    return None
print('B105 stairs',[(round(d['c'],1),d['n'],round(d['r'],3),round(d['o1'],2),round(d['end'],2),round(d['zt'],2),round(d['zb'],2)) for d in STAIRS])
# ---- materials
M=bpy.data.materials
def mk(name,col,rough):
    m=M.get(name)
    if m: return m
    m=M.new(name); m.use_nodes=True; b=m.node_tree.nodes.get('Principled BSDF'); b.inputs['Base Color'].default_value=(*col,1); b.inputs['Roughness'].default_value=rough; return m
conc=O['Footpaths_OSM'].data.materials[0]
mul=M.get('WS3_Mulch_bark_dark_brown') or M.get('WS87_median_mulch_dark_JOEphoto')
wallm=mk('WS105_retaining_wall_white_concrete_ortho2020_UNVERIFIED',(0.80,0.79,0.75),0.85)
band=mk('WS105_walkway_tan_joint_band_ortho2020_UNVERIFIED',(0.55,0.45,0.33),0.8)
steel=M.get('WS35_black_painted_steel') or mk('WS105_black_steel',(0.02,0.02,0.02),0.4)
coll=walk.users_collection[0]
def P(s,o,z): p,n=frame(s); q=p+n*o; return (float(q[0]),float(q[1]),float(z))
def obj(name,bm,mats):
    bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
    me=bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for m in mats: me.materials.append(m)
    ob=O.new(name,me); coll.objects.link(ob); return ob
def box(bm,s0,s1,o0,o1,z0,z1,mi=0):
    v=[bm.verts.new(P(s,o,z)) for z in (z0,z1) for s,o in ((s0,o0),(s1,o0),(s1,o1),(s0,o1))]
    for f in ((0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)):
        x=bm.faces.new([v[i] for i in f]); x.material_index=mi
def strip(bm,ss,ofn,zfn,cols,mi_fn=None,skirt=0.3):
    G=[]
    for s in ss: G.append([bm.verts.new(P(s,o,zfn(s,o))) for o in ofn(s,cols)])
    for i in range(len(ss)-1):
        for j in range(cols-1):
            f=bm.faces.new((G[i][j],G[i+1][j],G[i+1][j+1],G[i][j+1]))
            if mi_fn: f.material_index=mi_fn(0.5*(ss[i]+ss[i+1]))
    if skirt:
        for i in range(len(ss)-1):
            for j in (0,cols-1):
                a,b=G[i][j],G[i+1][j]; a2=bm.verts.new(a.co-Vector((0,0,skirt))); b2=bm.verts.new(b.co-Vector((0,0,skirt))); bm.faces.new((a,b,b2,a2))
        for r in (G[0],G[-1]):
            for j in range(cols-1):
                a,b=r[j],r[j+1]; a2=bm.verts.new(a.co-Vector((0,0,skirt))); b2=bm.verts.new(b.co-Vector((0,0,skirt))); bm.faces.new((a,b,b2,a2))
    return G
# 1) lower walkway
def wo0(s): return ow(s)+0.3 if wg(s)>0.02 else ow(s)+0.3
ss=np.round(np.arange(1.5,WS1+0.01,0.5),3)
def bandi(s): return 1 if (s%4.5)<0.4 else 0
bm=bmesh.new(); strip(bm,ss,lambda s,c: np.linspace(wo0(s)-0.05,OB,c),lambda s,o: zlow(s)+0.006*(o-wo0(s)),6,bandi,0.3)
wk=obj('WS105_Chapin_E_lower_walkway_concrete_LiDAR2023_ortho2020_UNVERIFIEDwidth',bm,[conc,band])
# 2) bed (skip stair zones incl. cheeks)
segs=[]; cur=[]
for s in np.round(np.arange(WS0,WS1+0.01,0.5),3):
    if instair(s) is None: cur.append(s)
    else:
        if len(cur)>1: segs.append(cur)
        cur=[]
if len(cur)>1: segs.append(cur)
# add exact stair-zone boundaries to segment ends
for st in STAIRS:
    for sg in segs:
        if abs(sg[-1]-(st['c']-HW-CW))<0.6: sg.append(st['c']-HW-CW)
        if abs(sg[0]-(st['c']+HW+CW))<0.6: sg.insert(0,st['c']+HW+CW)
bm=bmesh.new()
for sg in segs:
    sg=sorted(set(sg)); strip(bm,sg,lambda s,c: np.linspace(oE(s)-0.02, ow(s)+(0.3 if wg(s)<0.05 else 0.0)*(1-min(wg(s)*3,1))+0.02,c),bedz,7,None,0.4)
bed=obj('WS105_Chapin_E_bank_planting_bed_MULCH_ortho2020_LiDAR_UNVERIFIED',bm,[mul])
# 3) retaining walls (0.3 m), skip stair openings
bm=bmesh.new(); nw=0
for a,b,h in WALLS:
    s=a
    while s<b-1e-6:
        s1=min(s+0.5,b); sc=0.5*(s+s1)
        if instair(sc) is None and wg(sc)>0.05:
            top=zbend(sc)+0.10; box(bm,s,s1,ow(sc)-0.02,ow(sc)+0.30,zlow(sc)-0.15,top); nw+=1
        s=s1
wall=obj('WS105_Chapin_E_bank_retaining_wall_white_ortho2020_LiDARface_UNVERIFIED',bm,[wallm]); print('B105 wall pieces',nw)
# 4) stairs + cheeks + rails + landings
bm=bmesh.new(); bmc=bmesh.new(); bmr=bmesh.new()
for st in STAIRS:
    c,n,r,o1,zt,zb=st['c'],st['n'],st['r'],st['o1'],st['zt'],st['zb']
    for i in range(1,n):
        box(bm,c-HW,c+HW,o1+(i-1)*0.30,o1+i*0.30+0.02,zb-0.15,zt-i*r)
    le=max(st['end'],wo0(c))+0.05; box(bm,c-HW,c+HW,st['end'],le+0.3,zb-0.15,zb)  # landing onto walkway
    def tz(o): k=int(np.clip(np.floor((o-o1)/0.30)+1,1,n)); return zt-k*r if o>o1 else zt
    for side in (-1,1):
        s0=c+side*HW; s1=c+side*(HW+CW); ss_=min(s0,s1); se_=max(s0,s1)
        oo=np.arange(o1-0.02,le+0.01,0.3)
        for k in range(len(oo)-1):
            om=0.5*(oo[k]+oo[k+1]); sb=c+side*(HW+CW+0.05)
            topv=max(tz(oo[k+1])+0.25, (bedz(sb,om)+0.10) if om<ow(sb)+0.3 else -1e9)
            box(bmc,ss_,se_,oo[k],oo[k+1],zb-0.15,min(topv,zt+0.12))
        # rail on posts, 0.86 m above nosings, inside the cheek
        sr_=c+side*(HW-0.06); A=(o1+0.15,zt-r+0.86); Bp=(st['end']-0.15,zb+r+0.86)
        npost=max(2,int((Bp[0]-A[0])/1.2)+1)
        for k in range(npost):
            t=k/(npost-1); oo_=A[0]+t*(Bp[0]-A[0]); zz=A[1]+t*(Bp[1]-A[1]); box(bmr,sr_-0.025,sr_+0.025,oo_-0.025,oo_+0.025,tz(oo_),zz)
        # rail bar as a sloped prism
        v=[bmr.verts.new(P(sr_+ds,oo_,zz+dz)) for (oo_,zz) in (A,Bp) for ds,dz in ((-0.025,-0.02),(0.025,-0.02),(0.025,0.02),(-0.025,0.02))]
        for f in ((0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)): bmr.faces.new([v[i] for i in f])
stairs=obj('WS105_Chapin_E_bank_stairs_concrete_LiDAR2023_UNVERIFIEDrisers',bm,[conc])
cheek=obj('WS105_Chapin_E_bank_stair_cheek_walls_white_UNVERIFIED',bmc,[wallm])
rails=obj('WS105_Chapin_E_bank_stair_handrails_steel_UNVERIFIED',bmr,[steel])
# 5) shrubs in the bed (ortho: dark shrub masses), skip stairs/near stair cheeks
src=[o for o in O if o.name.startswith('WS99_bed_shrub_')]
random.seed(105); nsh=0
s=0.8
while s<39.5:
    if all(abs(s-st['c'])>HW+CW+0.6 for st in STAIRS):
        o=0.5*(oE(s)+ow(s))+random.uniform(-0.25,0.25); z=bedz(s,o)
        if ow(s)-oE(s)>1.2 and src:
            b=random.choice(src); n_=b.copy(); n_.name='WS105_bank_shrub_%02d_ortho2020_UNVERIFIED'%nsh; coll.objects.link(n_)
            n_.location=P(s,o,z-0.02); n_.rotation_euler=(0,0,random.uniform(0,6.28)); sc=random.uniform(0.75,0.95); n_.scale=tuple(x*sc for x in b.scale); nsh+=1
    s+=random.uniform(1.5,2.1)
print('B105 shrubs',nsh)
# 6) retire Footpaths_OSM faces inside the new footprint
fp=O['Footpaths_OSM']; bmf=bmesh.new(); bmf.from_mesh(fp.data); mw=fp.matrix_world; dl=[]
for f in bmf.faces:
    c=mw@f.calc_center_median(); s,o=so(np.array([c.x,c.y]))
    if WS0-0.3<=s<=WS1 and oE(max(s,0))+0.15<=o<=OB+0.2: dl.append(f)
bmesh.ops.delete(bmf,geom=dl,context='FACES'); lv=[v for v in bmf.verts if not v.link_faces]; bmesh.ops.delete(bmf,geom=lv,context='VERTS')
bmf.to_mesh(fp.data); fp.data.update(); bmf.free(); print('B105 fp faces removed',len(dl))
# 7) terrain re-seat under / beside the build
T=O.get('Terrain_LiDAR_DTM_1m')
if T is None: raise SystemExit('B105 no terrain (dry)')
TW,TM=getW(T); p0,_=frame(-3); p1,_=frame(44)
sel=np.where((TW[:,0]>min(p0[0],p1[0])-20)&(TW[:,0]<max(p0[0],p1[0])+20)&(TW[:,1]>min(p0[1],p1[1])-20)&(TW[:,1]<max(p0[1],p1[1])+20))[0]
nch=0; mx=0; mn=0
for k in sel:
    s,o=so(TW[k])
    if not (WS0-0.5<=s<=WS1+0.5): continue
    se=min(max(s,WS0),WS1); o1=oE(max(se,0.0))
    if o<o1+0.25 or o>16.5: continue
    st=instair(se)
    if o>OB: 
        lv_=lid(se,o); tgt=(zlow(se)-0.03)*(1-sm(OB,16.5,o))+(lv_ if lv_ is not None else TW[k,2])*sm(OB,16.5,o)
        tgt=min(tgt,zlow(se)-0.03+0.25*sm(OB,16.5,o))
    elif o>=ow(se)-1.0 or st is not None: tgt=zlow(se)-0.07
    else: tgt=bedz(se,o)-0.06
    d=tgt-TW[k,2]
    if abs(d)>0.005: TW[k,2]=tgt; nch+=1; mx=max(mx,d); mn=min(mn,d)
Mi=np.linalg.inv(TM); T.data.vertices.foreach_set('co',(TW@Mi[:3,:3].T+Mi[:3,3]).ravel()); T.data.update()
print('B105 terrain changed',nch,'max raise %.2f max lower %.2f'%(mx,mn))
rep=dict(stairs=STAIRS,walls=nw,shrubs=nsh,fp=len(dl),terr=nch,raise_=mx,lower=mn,bed_faces=len(bed.data.polygons),walk_faces=len(wk.data.polygons))
json.dump(rep,open(OUT+'build105.json','w'),default=float)
if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('B105 SAVED')
