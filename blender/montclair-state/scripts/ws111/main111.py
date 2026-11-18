# ws111: UNIFY #8 curb bridges, curb ramps at the band, College Ave S walks to brick corner aprons (UNIFY #9), entrance pavilions (LiDAR heights)
import bpy, bmesh, numpy as np, math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.geometry import delaunay_2d_cdt
R='/workspace/nj-scenes/montclair-state/'
D=np.load(R+'prep/ws79_normal_ave_dtm/normal_ave_dtm_1m.npz'); DT=D['dtm']; DX0=float(D['x0']); DY0=float(D['y0'])
def dtm(x,y):
    fx=x-DX0; fy=y-DY0; j=int(np.floor(fx)); i=int(np.floor(fy))
    if not (0<=i<DT.shape[0]-1 and 0<=j<DT.shape[1]-1): return None
    a=fx-j; b=fy-i
    return float(DT[i,j]*(1-a)*(1-b)+DT[i,j+1]*a*(1-b)+DT[i+1,j]*(1-a)*b+DT[i+1,j+1]*a*b)
A=np.array([-244.8,-239.3]);B=np.array([-256.1,-271.6]);d=(B-A)/np.linalg.norm(B-A);n=np.array([d[1],-d[0]])
def st(x,y): return (x-A[0])*d[0]+(y-A[1])*d[1],(x-A[0])*n[0]+(y-A[1])*n[1]
def W(s,t): p=A+d*s+n*t; return float(p[0]),float(p[1])
O=lambda p: next(o for o in bpy.data.objects if o.name.startswith(p))
cw=O('WS110_CollegeAve_S_end_to_NormalAve'); c102={'W':O('WS102_CollegeAve_S_curb_W'),'E':O('WS102_CollegeAve_S_curb_E')}
c110={'W':O('WS110_CollegeAve_S_end_curb_W'),'E':O('WS110_CollegeAve_S_end_curb_E')}
t102=O('WS102_CollegeAve_S_carriageway'); nwalk=O('WS110_NormalAve_sidewalk'); nverge=O('WS110_NormalAve_verge')
col=bpy.data.collections.new('WS111_CollegeAve_S_walks_aprons_pavilions'); bpy.context.scene.collection.children.link(col)
MAT=bpy.data.materials
def mat(*keys):
    for k in keys:
        m=MAT.get(k)
        if m: return m
    for k in keys:
        for m in MAT:
            if k.lower() in m.name.lower(): return m
    return None
M_curb=MAT['WS27_curb_concrete_UNVERIFIED']; M_conc=MAT.get('Paving_concrete'); M_brick=MAT['WS27_brick_crosswalk_2020ortho']
def bvh_of(o):
    me=o.data; mw=o.matrix_world
    return BVHTree.FromPolygons([tuple(mw@v.co) for v in me.vertices],[tuple(p.vertices) for p in me.polygons])
def link(name,bm,m):
    me=bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    if isinstance(m,(list,tuple)):
        for mm in m: me.materials.append(mm)
    else: me.materials.append(m)
    ob=bpy.data.objects.new(name,me); col.objects.link(ob); return ob
NEW=[]
# ---------- 1. UNIFY #8: curb bridges s 3.88 -> 4.39
for side in ('W','E'):
    a=np.array([c102[side].matrix_world@v.co for v in c102[side].data.vertices]); sa,_=st(a[:,0],a[:,1]); ea=a[sa>sa.max()-0.05]
    b=np.array([c110[side].matrix_world@v.co for v in c110[side].data.vertices])[:4]
    def ring(r):
        s_,t_=st(r[:,0],r[:,1]); c=np.array([t_.mean(),r[:,2].mean()]); ang=np.arctan2(r[:,2]-c[1],t_-c[0]); return r[np.argsort(ang)],t_[np.argsort(ang)]
    ra,ta=ring(ea); rb,tb=ring(b)
    bm=bmesh.new(); va=[bm.verts.new(tuple(p)) for p in ra]; vb=[bm.verts.new(tuple(p)) for p in rb]
    for i in range(4): bm.faces.new((va[i],va[(i+1)%4],vb[(i+1)%4],vb[i]))
    bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
    o=link('WS111_CollegeAve_S_curb_%s_bridge_s88_UNIFY8'%side,bm,M_curb); NEW.append(o)
    print('E111 bridge',side,len(ea),np.round(ta,2).tolist(),np.round(tb,2).tolist(),'dz',round(float(ra[:,2].max()-rb[:,2].max()),3))
# ---------- 2. curb cut ramps at the brick band (s 18.2..20.2)
bc=bvh_of(cw); S0,S1,TP=18.2,20.2,0.8
def wcut(s):
    if S0<=s<=S1: return 1.0
    u=(S0-s)/TP if s<S0 else (s-S1)/TP
    if u>=1: return 0.0
    u=1-u; return u*u*(3-2*u)
for side,tr in (('W',3.05),('E',-3.30)):
    o=c110[side]; me=o.data; mw=o.matrix_world; mi=mw.inverted(); nlow=0
    for k in range(0,len(me.vertices),4):
        row=me.vertices[k:k+4]; p=mw@row[1].co; s,_=st(p.x,p.y); w=wcut(s)
        if w<=0: continue
        x,y=W(s,tr); h=bc.ray_cast(Vector((x,y,p.z+5)),Vector((0,0,-1)),20)
        if h[0] is None: continue
        zr=h[0].z+0.015
        for j in (1,2):
            q=mw@row[j].co; q.z=q.z-w*(q.z-zr); row[j].co=mi@q
        nlow+=1
    me.update(); print('E111 cut',side,nlow)
# curb back-top polyline per side (after cut)
def back(side):
    o=c110[side]; me=o.data; mw=o.matrix_world
    return np.array([tuple(mw@me.vertices[k+2].co) for k in range(0,len(me.vertices),4)])
BK={s:back(s) for s in ('W','E')}
def curbtop(side,s):
    a=np.array([c102[side].matrix_world@v.co for v in c102[side].data.vertices]); sa,ta=st(a[:,0],a[:,1])
    bk=BK[side]; sb,tb=st(bk[:,0],bk[:,1]); m=sb<16.5
    ss=np.r_[sa,sb[m]]; zz=np.r_[a[:,2],bk[m,2]]; tt=np.r_[ta,tb[m]]
    # top of curb at s: max z among verts within 0.3 m
    sel=np.abs(ss-s)<0.3
    zt=zz[sel].max(); tback=tt[sel][np.argmax(np.abs(tt[sel]))]
    return float(zt),float(tback)
# ---------- 3. College Ave S walks in the gap (s ~1.9/4.4 -> 16)
SA=16.0; WALKEND={}
w103=O('WS103_CollegeAve_S_W_sidewalk'); a=np.array([w103.matrix_world@v.co for v in w103.data.vertices]); sa,ta=st(a[:,0],a[:,1])
er=a[(sa>sa.max()-0.05)]; er_t=st(er[:,0],er[:,1])[1]; Wst=float(sa.max()); Wout=float(er_t.max())
ta2=st(*np.array([t102.matrix_world@v.co for v in t102.data.vertices])[:, :2].T)
c=np.array([t102.matrix_world@v.co for v in t102.data.vertices]); cs,ct=st(c[:,0],c[:,1])
ee=(ct<-3.75)&(ct>-9)&(cs>-3)
Est=float(cs[ee].max()) if ee.any() else 4.39
ee2=ee&(cs>Est-0.05)
Eout=float(ct[ee2].min()) if ee.any() else -6.3
if Eout>-5.0: Eout=-6.3
print('E111 walk starts W s %.2f tout %.2f | E s %.2f tout %.2f'%(Wst,Wout,Est,Eout))
for side,s0,tout0,wfin in (('W',Wst,Wout,2.9),('E',Est,Eout,2.7)):
    sg=1 if side=='W' else -1
    ss=list(np.arange(s0,SA,0.5))+[SA]
    bm=bmesh.new(); top=[];bot=[]
    for s in ss:
        zt,tb=curbtop(side,s); w0=abs(tout0-tb); u=min(max((s-s0)/6.0,0),1); u=u*u*(3-2*u); w=w0*(1-u)+wfin*u
        r=[];rb=[]
        for f in (0,0.5,1):
            t=tb+sg*w*f; x,y=W(s,t); z=zt+0.02*w*f; r.append(bm.verts.new((x,y,z)))
        x,y=W(s,tb+sg*w); rb.append(bm.verts.new((x,y,zt+0.02*w-0.30)))
        top.append(r); bot.append(rb)
    for i in range(len(ss)-1):
        for j in range(2): bm.faces.new((top[i][j],top[i][j+1],top[i+1][j+1],top[i+1][j]))
        bm.faces.new((top[i][2],bot[i][0],bot[i+1][0],top[i+1][2]))
    bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
    for f in bm.faces:
        if f.normal.z<-0.5: f.normal_flip()
    WALKEND[side]=[tuple(v.co) for v in top[-1]]
    o=link('WS111_CollegeAve_S_%s_walk_gap_to_apron_concrete_ortho2020_UNVERIFIEDwidth'%side,bm,M_conc); NEW.append(o)
    print('E111 walk',side,len(ss),'z0 %.2f z1 %.2f'%(top[0][0].co.z if False else 0,0))
# ---------- 4. brick corner aprons with ramps
def pip(px,py,poly):
    ins=False; j=len(poly)-1
    for i in range(len(poly)):
        xi,yi=poly[i]; xj,yj=poly[j]
        if ((yi>py)!=(yj>py)) and (px<(xj-xi)*(py-yi)/(yj-yi+1e-12)+xi): ins=not ins
        j=i
    return ins
bw=bvh_of(nwalk)
def zwalk(x,y):
    h=bw.ray_cast(Vector((x,y,140)),Vector((0,0,-1)),60); return h[0].z if h[0] else None
APR={}
for side in ('W','E'):
    bk=BK[side]; sb,tb=st(bk[:,0],bk[:,1]); k0=int(np.argmax(sb>=SA))
    arc=[tuple(p) for p in bk[k0:]]
    end=np.array(arc[-1][:2])
    if side=='W': u=np.array([-0.987,-0.162]); out=np.array([-0.162,0.987]); ext=1.2; Xfar=-265.0
    else: u=np.array([0.971,-0.240]); out=np.array([0.240,0.971]); ext=1.2; Xfar=-239.4
    Q1=end+u*ext; Q2=Q1+out*1.6
    t_=(Xfar-Q2[0])/u[0]; Q3=Q2+u*t_
    we=WALKEND[side]; wout=np.array(we[2][:2]); win=np.array(we[0][:2])
    # Q4: from Q3 go 'out' until level with the walk end (project)
    k=np.dot(wout-Q3,out); Q4=Q3+out*(k+(1.0 if side=='W' else 0.3))
    poly=[(p[0],p[1]) for p in arc]+[tuple(Q1),tuple(Q2),tuple(Q3),tuple(Q4),tuple(wout)]
    if side=='E': poly=poly[::-1]
    # anchors (residual over dtm)
    anc=[(p[0],p[1],p[2]) for p in arc]+[tuple(v) for v in we]
    for q in (Q1,Q2,Q3):
        z=zwalk(q[0],q[1]); 
        if z is not None: anc.append((q[0],q[1],z+0.006))
    an=np.array(anc); res=np.array([z-(dtm(x,y) or z) for x,y,z in an])
    def zat(x,y):
        dd=np.hypot(an[:,0]-x,an[:,1]-y)+0.05; w=1/dd**2.5; return (dtm(x,y) or float(np.median(an[:,2])))+float((w*res).sum()/w.sum())
    xs=[p[0] for p in poly]; ys=[p[1] for p in poly]
    pts=[tuple(p) for p in poly]; nb=len(pts)
    for gx in np.arange(min(xs),max(xs),0.5):
        for gy in np.arange(min(ys),max(ys),0.5):
            if pip(gx,gy,poly):
                dmin=min(math.hypot(gx-p[0],gy-p[1]) for p in poly)
                if dmin>0.25: pts.append((gx,gy))
    edges=[(i,(i+1)%nb) for i in range(nb)]
    vo,eo,fo,_,_,_=delaunay_2d_cdt([Vector(p) for p in pts],edges,[],0,1e-5)
    bm=bmesh.new(); vv=[]
    for i,p in enumerate(vo):
        z=None
        for (ax,ay,az) in anc:
            if abs(ax-p.x)<1e-4 and abs(ay-p.y)<1e-4: z=az
        if z is None: z=zat(p.x,p.y)
        vv.append(bm.verts.new((p.x,p.y,z)))
    for f in fo:
        cx=sum(vo[i].x for i in f)/len(f); cy=sum(vo[i].y for i in f)/len(f)
        if pip(cx,cy,poly):
            try: bm.faces.new([vv[i] for i in f])
            except ValueError: pass
    bmesh.ops.remove_doubles(bm,verts=bm.verts,dist=1e-4)
    for f in bm.faces:
        if f.normal.z<0: f.normal_flip()
    be=[e for e in bm.edges if e.is_boundary]
    ex=bmesh.ops.extrude_edge_only(bm,edges=be)
    for v in [g for g in ex['geom'] if isinstance(g,bmesh.types.BMVert)]: v.co.z-=0.15
    lone=[v for v in bm.verts if not v.link_faces]; bmesh.ops.delete(bm,geom=lone,context='VERTS')
    o=link('WS111_CollegeAve_%s_corner_apron_brick_ramp_ortho2020_UNVERIFIED'%side,bm,M_brick); NEW.append(o)
    APR[side]=poly; print('E111 apron',side,len(o.data.vertices),len(o.data.polygons))
# remove Normal walk / verge faces under the aprons (UNIFY #9)
for ob in (nwalk,nverge):
    me=ob.data; bm=bmesh.new(); bm.from_mesh(me); mw=ob.matrix_world
    kill=[f for f in bm.faces if any(pip(*(tuple(mw@f.calc_center_median())[:2]),APR[s]) for s in APR)]
    bmesh.ops.delete(bm,geom=kill,context='FACES'); bm.to_mesh(me); bm.free(); me.update(); print('E111 removed',ob.name[:30],len(kill))
# ---------- 5. pavilions (2023 LiDAR: eave ~3.85 m, apex ~4.9 m above ground, ~5.5 m square roofs; ortho red pyramid tile roofs)
M_st=mat('WS107_Chapin_stucco','stucco','Stucco'); M_tile=mat('WS107_Chapin_red_tile','red_tile','tile','Tile')
print('E111 mats',M_st and M_st.name,M_tile and M_tile.name)
ang=math.atan2(d[1],d[0])
for side,(cx,cy) in (('W',(-261.0,-255.0)),('E',(-241.9,-261.5))):
    zg=zat_g=dtm(cx,cy)
    h=None
    for oo in NEW:
        if 'apron' in oo.name and oo.name.startswith('WS111_CollegeAve_%s'%side):
            h=bvh_of(oo).ray_cast(Vector((cx,cy,150)),Vector((0,0,-1)),80)
    z0=h[0].z if h and h[0] else zg
    bm=bmesh.new()
    def box(c,hx,hy,z1,z2):
        r=bmesh.ops.create_cube(bm,size=1.0)['verts']
        for v in r: v.co.x*=2*hx; v.co.y*=2*hy; v.co.z=(z1 if v.co.z<0 else z2)
        for v in r: v.co.x+=c[0]; v.co.y+=c[1]
    for px in (-1,1):
        for py in (-1,1): box((px*1.95,py*1.95),0.32,0.32,-0.3,3.55)
    for py in (-1,1): box((0,py*1.95),2.27,0.32,2.95,3.85)
    for px in (-1,1): box((px*1.95,0),0.32,1.63,2.95,3.85)
    box((0,0),0.32*0+2.27,2.27,3.55,3.85)
    rot=__import__('mathutils').Matrix.Rotation(ang,4,'Z'); bmesh.ops.transform(bm,matrix=rot,verts=bm.verts)
    bmesh.ops.translate(bm,vec=Vector((cx,cy,z0)),verts=bm.verts)
    o=link('WS111_entrance_pavilion_%s_stucco_LiDAR2023h_UNVERIFIEDform'%side,bm,M_st or M_curb); NEW.append(o)
    bm=bmesh.new(); hw=2.75; zE=z0+3.85; zA=z0+4.9
    cs_=[(-hw,-hw),(hw,-hw),(hw,hw),(-hw,hw)]
    top=bm.verts.new((0,0,zA)); bs=[bm.verts.new((x,y,zE)) for x,y in cs_]; bl=[bm.verts.new((x,y,zE-0.12)) for x,y in cs_]
    for i in range(4):
        bm.faces.new((bs[i],bs[(i+1)%4],top)); bm.faces.new((bl[i],bl[(i+1)%4],bs[(i+1)%4],bs[i]))
    bm.faces.new(bl[::-1])
    bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
    bmesh.ops.transform(bm,matrix=rot,verts=bm.verts); bmesh.ops.translate(bm,vec=Vector((cx,cy,0)),verts=bm.verts)
    o=link('WS111_entrance_pavilion_%s_pyramid_tile_roof_LiDAR2023_ortho2020'%side,bm,M_tile or M_brick); NEW.append(o)
    print('E111 pav',side,'z0 %.2f'%z0)
# ---------- 6. cap terrain under new paving
pav=[o for o in NEW if 'walk' in o.name or 'apron' in o.name or 'bridge' in o.name]
bv=[bvh_of(o) for o in pav]
for tn in ('Terrain_LiDAR_DTM_1m','WS110_ground_patch'):
    to=O(tn); me=to.data; mw=to.matrix_world; mi=mw.inverted(); ncap=0
    for v in me.vertices:
        p=mw@v.co
        if not (-268<p.x<-236 and -270<p.y<-238): continue
        zmin=None
        for dx,dy in ((0,0),(0.4,0),(-0.4,0),(0,0.4),(0,-0.4)):
            for b in bv:
                h=b.ray_cast(Vector((p.x+dx,p.y+dy,150)),Vector((0,0,-1)),80)
                if h[0] is not None and h[0].z>p.z-2.0:
                    zz=h[0].z; zmin=zz if zmin is None else min(zmin,zz)
        if zmin is not None and p.z>zmin-0.05:
            p.z=zmin-0.05; v.co=mi@p; ncap+=1
    me.update(); print('E111 cap',tn,ncap)
bpy.ops.wm.save_mainfile(); print('E111 SAVED')
