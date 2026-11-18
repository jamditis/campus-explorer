import bpy,bmesh,math,os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
O=bpy.data.objects
def wv(o): m=o.matrix_world; return [m@v.co for v in o.data.vertices]
def bvh(n):
    o=O[n]; e=o.evaluated_get(dg); me=e.to_mesh(); bm=bmesh.new(); bm.from_mesh(me); bm.transform(o.matrix_world)
    t=BVHTree.FromBMesh(bm); bm.free(); e.to_mesh_clear(); return t
def zz(t,x,y):
    r=t.ray_cast(Vector((x,y,300)),Vector((0,0,-1)),400); return r[0].z if r[0] else None
for n in ('COLE_plaza_deck_bs','COLE_plaza_edge_bs','Footpaths_OSM','OZ_walk_joints_auto_GN_UNVERIFIED','PA_walk_panel_tone_chips_UNVERIFIED','WS27_CollegeAve_curb_left_UNVERIFIED','WS27_CollegeAve_carriageway_2020ortho','Terrain_LiDAR_DTM_1m'):
    oo=[o for o in O if o.name.startswith(n[:28])]
    for o in oo: print('F40 obj',o.name,'mods',[(m.type,m.name) for m in o.modifiers],'mats',[s.material.name if s.material else None for s in o.material_slots][:4],'nv',len(o.data.vertices) if o.type=='MESH' else '-')
ST=O['WS35_Kasser_terrace_steps_concrete_5risers_UNVERIFIED']; CW=O['WS35_Kasser_steps_cheek_walls_UNVERIFIED']; RL=O['WS35_Kasser_steps_pipe_handrails_slim_UNVERIFIED']
LD=O.get('WS39_Kasser_steps_foot_landing_concrete_UNVERIFIED')
# ---- east curb line (curb_left) ----
CL=O['WS27_CollegeAve_curb_left_UNVERIFIED']; clv=wv(CL)
def curb(y):
    c=[p for p in clv if abs(p.y-y)<0.6 and -215<p.x<-185]
    if not c: return None
    xm=max(p.x for p in c); zt=max(p.z for p in c if p.x>xm-0.4)
    return xm,zt
XC={}
for i in range(-120,-50):
    y=i*1.0; r=curb(y)
    if r: XC[i]=r
print('F40 curb', {k:(round(v[0],2),round(v[1],2)) for k,v in XC.items() if -104<=k<=-76})
def xc_at(y):
    i0=math.floor(y); i1=i0+1
    if i0 in XC and i1 in XC:
        t=y-i0; return XC[i0][0]*(1-t)+XC[i1][0]*t, XC[i0][1]*(1-t)+XC[i1][1]*t
    k=min(XC,key=lambda k:abs(k-y)); return XC[k]
# ---- steps placement ----
def bbw(o):
    b=[o.matrix_world@Vector(c) for c in o.bound_box]; return min(p.x for p in b),max(p.x for p in b),min(p.y for p in b),max(p.y for p in b),min(p.z for p in b),max(p.z for p in b)
cx0,cx1,cy0,cy1,_,cz1=bbw(CW); sx0,sx1,sy0,sy1,sz0,sz1=bbw(ST)
SW=2.0
YA,YB=cy0-1.6,cy1+1.6
xcmax=max(xc_at(YA+k*0.25)[0] for k in range(int((YB-YA)/0.25)+1))
XB=xcmax+SW
zcm=sum(xc_at(y)[1] for y in (cy0,(cy0+cy1)/2,cy1))/3
SB=zcm+0.03
def S(x,y):   # sidewalk top: flush with curb top at the curb, level SB at the step foot
    xc,zc=xc_at(y); t=min(max((x-xc)/max(XB-xc,0.5),0),1); return zc+(SB-zc)*t
OLD_BASE=127.06
dx=XB-cx0; dz=SB-OLD_BASE
print('F40 xcmax %.2f XB %.2f SB %.2f dx %.2f dz %.2f stepsz %.2f..%.2f'%(xcmax,XB,SB,dx,dz,sz0,sz1))
for o in (ST,CW,RL):
    o.matrix_world.translation+=Vector((dx,0,dz))
dg.update()
sx0,sx1,sy0,sy1,sz0,sz1=bbw(ST); cx0,cx1,cy0,cy1,_,cz1=bbw(CW)
XT=sx1; ZT=sz1  # top tread level
print('F40 steps now x %.2f..%.2f y %.2f..%.2f top %.2f'%(sx0,sx1,sy0,sy1,ZT))
OLD=(-203.25,-198.4,-97.9,-86.4)
def inold(x,y): return OLD[0]<x<OLD[1] and OLD[2]<y<OLD[3]
# ---- restore road verts tucked under the old landing/steps (anisotropic IDW from outside) ----
for name in ('WS27_CollegeAve_carriageway_2020ortho','WS27_CollegeAve_curb_right_UNVERIFIED','WS27_CollegeAve_curb_left_UNVERIFIED'):
    o=O[name]; m=o.matrix_world; mi=m.inverted(); P=[m@v.co for v in o.data.vertices]
    outs=[p for p in P if not inold(p.x,p.y) and OLD[0]-3<p.x<OLD[1]+3 and OLD[2]-6<p.y<OLD[3]+6]
    c=0
    for v,p in zip(o.data.vertices,P):
        if not inold(p.x,p.y) or not outs: continue
        sw=0; sz=0
        for q in outs:
            d2=((q.x-p.x)*4)**2+(q.y-p.y)**2+0.01; w=1/d2**1.5; sw+=w; sz+=w*q.z
        nz=sz/sw
        if nz-p.z>0.005: v.co=mi@Vector((p.x,p.y,nz)); c+=1
    o.data.update(); print('F40 road restored',name,c)
if LD: bpy.data.objects.remove(LD,do_unlink=True); print('F40 removed ws39 landing')
dg.update()
# ---- deck regrade field: raise deck near steps top so it meets the top tread ----
TD0=bvh('COLE_plaza_deck_bs')
L=5.0; YF=3.0
ztop_y={}
def raise_amt(x,y):
    if x<XT-0.3: base=1.0
    else:
        t=min((x-XT+0.3)/L,1.0); base=1-t*t*(3-2*t)
    if base<=0: return 0
    dyo=max(cy0-y,0,y-cy1)
    if dyo>=YF: return 0
    ty=1-dyo/YF; wy=ty*ty*(3-2*ty)
    zd=zz(TD0,XT+0.05,min(max(y,cy0),cy1))
    if zd is None: return 0
    return max(0.0,(ZT-0.01)-zd)*base*wy
RCACHE={}
def R(x,y):
    k=(round(x,1),round(y,1))
    if k not in RCACHE: RCACHE[k]=raise_amt(x,y)
    return RCACHE[k]
def cutx(y):   # deck/walk removed west of this line
    if YA<=y<=YB: return XB
    return xc_at(y)[0]+0.15
def in_steps(x,y): return sx0-0.05<x<sx1+0.02 and cy0<y<cy1
REG=(XB-1,XT+L+0.5,cy0-YF-0.5,cy1+YF+0.5)
TT0=bvh('Terrain_LiDAR_DTM_1m')
# ---- trim + regrade deck/edge/walk meshes ----
for name in ('COLE_plaza_deck_bs','COLE_plaza_edge_bs','Footpaths_OSM','OZ_walk_joints_auto_GN_UNVERIFIED','PA_walk_panel_tone_chips_UNVERIFIED'):
    o=O.get(name)
    if not o or o.type!='MESH': print('F40 missing',name); continue
    m=o.matrix_world; mi=m.inverted()
    bm=bmesh.new(); bm.from_mesh(o.data)
    kill=[]
    for f in bm.faces:
        c=m@f.calc_center_median()
        if c.y<-125 or c.y>-55 or c.x>-180: continue
        deckish=name.startswith('COLE')
        if deckish and c.x<cutx(c.y): kill.append(f)
        elif in_steps(c.x,c.y): kill.append(f)
        elif (not deckish) and YA<=c.y<=YB and xc_at(c.y)[0]+0.05<c.x<XB+0.05: kill.append(f)
    bmesh.ops.delete(bm,geom=kill,context='FACES')
    mv=0
    for v in bm.verts:
        p=m@v.co
        if REG[0]<p.x<REG[1] and REG[2]<p.y<REG[3]:
            r=R(p.x,p.y)
            if r>0.003: v.co=mi@Vector((p.x,p.y,p.z+r)); mv+=1
    bm.to_mesh(o.data); bm.free(); o.data.update(); print('F40 trim',name,'faces',len(kill),'raised',mv)
dg.update()
# ---- fascia along the deck cut ----
o=O['COLE_plaza_deck_bs']; m=o.matrix_world
bm=bmesh.new(); bm.from_mesh(o.data); bm.transform(m)
fv=[];ff=[]
for e in bm.edges:
    if not e.is_boundary: continue
    a,b=e.verts[0].co.copy(),e.verts[1].co.copy(); my=(a.y+b.y)/2; mx=(a.x+b.x)/2
    if not (-104<my<-60): continue
    if abs(mx-cutx(my))>1.0 and not (abs(mx-sx0)<0.6 and cy0-0.3<my<cy1+0.3): continue
    za=min(S(a.x,a.y),a.z)-0.06; zb=min(S(b.x,b.y),b.z)-0.06
    if a.z-za<0.08 and b.z-zb<0.08: continue
    i=len(fv); fv+= [tuple(a),tuple(b),(b.x,b.y,zb),(a.x,a.y,za)]; ff.append((i,i+1,i+2,i+3))
bm.free()
me=bpy.data.meshes.new('WS40_Cole_deck_cut_fascia'); me.from_pydata(fv,[],ff); me.update()
fo=bpy.data.objects.new('WS40_Cole_deck_cut_fascia_concrete_UNVERIFIED',me); sc.collection.objects.link(fo)
for c in CW.users_collection:
    if fo.name not in c.objects: c.objects.link(fo)
if sc.collection.objects.get(fo.name) and CW.users_collection and CW.users_collection[0]!=sc.collection: sc.collection.objects.unlink(fo)
fm=CW.material_slots[0].material if CW.material_slots else None
if fm: me.materials.append(fm)
print('F40 fascia quads',len(ff),'mat',fm.name if fm else None)
# ---- new sidewalk between curb and steps ----
mat=bpy.data.materials.get('WS3_Concrete_panels_sawcut') or fm
verts=[];faces=[]; NY=int((YB-YA)/0.5)+1; NX=6
for j in range(NY):
    y=YA+(YB-YA)*j/(NY-1); xc,_=xc_at(y); x0=xc-0.02
    for i in range(NX):
        x=x0+(XB+0.03-x0)*i/(NX-1); verts.append((x,y,S(x,y)))
for j in range(NY-1):
    for i in range(NX-1):
        a=j*NX+i; faces.append((a,a+1,a+NX+1,a+NX))
# skirt down 0.2 m on the four edges
top=len(verts)
ring=[j*NX for j in range(NY)]+[ (NY-1)*NX+i for i in range(1,NX)]+[j*NX+NX-1 for j in range(NY-2,-1,-1)]+[i for i in range(NX-2,0,-1)]
for k in ring: x,y,z=verts[k]; verts.append((x,y,z-0.2))
for k in range(len(ring)):
    a=ring[k]; b=ring[(k+1)%len(ring)]; faces.append((b,a,top+k,top+(k+1)%len(ring)))
me=bpy.data.meshes.new('WS40_CollegeAve_sidewalk'); me.from_pydata(verts,[],faces); me.update(); me.materials.append(mat)
so=bpy.data.objects.new('WS40_CollegeAve_east_sidewalk_to_Kasser_steps_concrete_OSM_JOE',me)
for c in CW.users_collection: c.objects.link(so)
print('F40 sidewalk x %.2f..%.2f y %.2f..%.2f z %.2f..%.2f mat %s'%(min(v[0] for v in verts[:top]),max(v[0] for v in verts[:top]),YA,YB,min(v[2] for v in verts[:top]),max(v[2] for v in verts[:top]),mat.name if mat else None))
def under_sw(x,y): return YA-0.05<y<YB+0.05 and xc_at(y)[0]-0.05<x<XB+0.1
# ---- terrain: under sidewalk/steps, regrade field, old pad ----
T=O['Terrain_LiDAR_DTM_1m']; tm=T.matrix_world; ti=tm.inverted(); mv=0
for v in T.data.vertices:
    p=tm@v.co
    if not (-206<p.x<-178 and -106<p.y<-78): continue
    nz=p.z
    if under_sw(p.x,p.y) or in_steps(p.x,p.y): nz=min(nz,S(min(p.x,XB),p.y)-0.10)
    elif REG[0]<p.x<REG[1] and REG[2]<p.y<REG[3]: nz=p.z+R(p.x,p.y)
    if abs(nz-p.z)>0.003: v.co=ti@Vector((p.x,p.y,nz)); mv+=1
T.data.update(); print('F40 terrain moved',mv)
dg.update(); TT1=bvh('Terrain_LiDAR_DTM_1m')
for o in list(O):
    if o.type!='MESH' or o.library or not any(k in o.name.lower() for k in ('grass','lawn')): continue
    mw=o.matrix_world; ob=[mw@Vector(cc) for cc in o.bound_box]
    if max(q.x for q in ob)<-206 or min(q.x for q in ob)>-178 or max(q.y for q in ob)<-106 or min(q.y for q in ob)>-78: continue
    if len(o.data.vertices)>300000: print('F40 skip big',o.name); continue
    bm=bmesh.new(); bm.from_mesh(o.data); mi=mw.inverted(); cnt=0; kill=[]
    for vv in bm.verts:
        p=mw@vv.co
        if not (-206<p.x<-178 and -106<p.y<-78): continue
        if under_sw(p.x,p.y) or in_steps(p.x,p.y): kill.append(vv); continue
        a0=zz(TT0,p.x,p.y); a1=zz(TT1,p.x,p.y)
        if a0 is None or a1 is None or abs(a1-a0)<0.003: continue
        vv.co=mi@Vector((p.x,p.y,p.z+a1-a0)); cnt+=1
    bmesh.ops.delete(bm,geom=kill,context='VERTS'); bm.to_mesh(o.data); bm.free(); o.data.update()
    print('F40 grass',o.name,'reseat',cnt,'removed',len(kill))
# ---- posts/chain in the sidewalk ----
for name in ('WS35_CollegeAve_bed_posts_black_PHOTO_JOE_20261110','WS35_CollegeAve_bed_chain_black_PHOTO_JOE_20261110'):
    o=O.get(name)
    if not o: continue
    mw=o.matrix_world; bm=bmesh.new(); bm.from_mesh(o.data); bm.verts.ensure_lookup_table()
    seen=set(); kill=[]
    for v in bm.verts:
        if v in seen: continue
        isl=[];st=[v];seen.add(v)
        while st:
            a=st.pop(); isl.append(a)
            for e in a.link_edges:
                b=e.other_vert(a)
                if b not in seen: seen.add(b); st.append(b)
        c=sum((mw@a.co for a in isl),Vector())/len(isl)
        if (YA-1<c.y<YB+1 and c.x>xc_at(c.y)[0]-0.3) or c.x>cutx(c.y)-0.3 and -104<c.y<-60: kill+=isl
    bmesh.ops.delete(bm,geom=kill,context='VERTS'); bm.to_mesh(o.data); bm.free(); o.data.update(); print('F40 removed parts verts',name,len(kill))
dg.update(); TD1=bvh('COLE_plaza_deck_bs')
for y in (-96,-92,-88):
    print('F40 prof y',y,'deck',[(x,round(zz(TD1,x,y),2) if zz(TD1,x,y) else None) for x in range(-196,-180,1)],'S',round(S(XB,y),2),'top',round(ZT,2))
if os.environ.get('SAVE')=='1':
    bpy.ops.wm.save_mainfile(); print('F40 SAVED')
