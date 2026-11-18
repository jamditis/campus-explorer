import bpy, bmesh, math, os, random
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree
random.seed(35)
sc=bpy.context.scene
log=[]
def L(*a):
    s=' '.join(str(x) for x in a); print('B35',s,flush=True); log.append(s)
# ---------- 1. delete clunky panels/steps ----------
for n in ('COLE_plaza_west_steps_bu','COLE_plaza_west_rail_N_bu','COLE_plaza_west_rail_mid_bu','COLE_plaza_west_rail_S_bu'):
    o=bpy.data.objects.get(n)
    if o: bpy.data.objects.remove(o,do_unlink=True); L('deleted',n)
dg=bpy.context.evaluated_depsgraph_get()
def bvh(name):
    o=bpy.data.objects.get(name)
    if not o: return None
    e=o.evaluated_get(dg); m=e.to_mesh()
    bm=bmesh.new(); bm.from_mesh(m); bm.transform(o.matrix_world)
    t=BVHTree.FromBMesh(bm); bm.free(); e.to_mesh_clear(); return t
T={n:bvh(n) for n in ('Terrain_LiDAR_DTM_1m','COLE_plaza_deck_bs','COLE_plaza_edge_bs','Footpaths_OSM','WS27_CollegeAve_curb_left_UNVERIFIED','WS27_CollegeAve_carriageway_2020ortho','Roads_OSM','COLE_planting_beds_smooth_bu')}
T={k:v for k,v in T.items() if v}
def hit(x,y,names):
    best=None
    for n in names:
        t=T.get(n)
        if not t: continue
        r=t.ray_cast(Vector((x,y,200)),Vector((0,0,-1)))
        if r[0] is not None and (best is None or r[0].z>best[0]): best=(r[0].z,n)
    return best
ALL=list(T.keys())
COL=bpy.data.collections.new('WS35_Kasser_Cole_frontage_20261110ws35'); sc.collection.children.link(COL)
def link(o): COL.objects.link(o); return o
# ---------- materials ----------
def mat(name,base,rough,metal=0.0,noise=None):
    m=bpy.data.materials.get(name)
    if m: return m
    m=bpy.data.materials.new(name); m.use_nodes=True; nt=m.node_tree; p=nt.nodes['Principled BSDF']
    p.inputs['Base Color'].default_value=(*base,1); p.inputs['Roughness'].default_value=rough; p.inputs['Metallic'].default_value=metal
    if noise:
        tc=nt.nodes.new('ShaderNodeTexCoord'); nz=nt.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value=noise[0]; nz.inputs['Detail'].default_value=8
        cr=nt.nodes.new('ShaderNodeValToRGB'); cr.color_ramp.elements[0].color=(*[c*noise[1] for c in base],1); cr.color_ramp.elements[1].color=(*[min(1,c*noise[2]) for c in base],1)
        nt.links.new(tc.outputs['Object'],nz.inputs['Vector']); nt.links.new(nz.outputs['Fac'],cr.inputs['Fac']); nt.links.new(cr.outputs['Color'],p.inputs['Base Color'])
        rr=nt.nodes.new('ShaderNodeMapRange'); rr.inputs['To Min'].default_value=rough*0.75; rr.inputs['To Max'].default_value=min(1,rough*1.25)
        nt.links.new(nz.outputs['Fac'],rr.inputs['Value']); nt.links.new(rr.outputs['Result'],p.inputs['Roughness'])
        bp=nt.nodes.new('ShaderNodeBump'); bp.inputs['Strength'].default_value=0.15; nt.links.new(nz.outputs['Fac'],bp.inputs['Height']); nt.links.new(bp.outputs['Normal'],p.inputs['Normal'])
    return m
M_conc=mat('WS35_concrete_steps',(0.62,0.60,0.56),0.8,noise=(18,0.85,1.1))
M_pipe=mat('WS35_black_painted_steel',(0.02,0.02,0.022),0.35,metal=0.6)
M_bronze=mat('WS35_dark_bronze_patina',(0.045,0.036,0.028),0.42,metal=1.0,noise=(9,0.55,1.6))
M_gran=mat('WS35_grey_granite',(0.40,0.395,0.385),0.7,noise=(60,0.6,1.35))
M_box=mat('WS35_boxwood',(0.035,0.085,0.025),0.75,noise=(30,0.6,1.6))
M_mulch=mat('WS35_mulch',(0.085,0.05,0.03),0.95,noise=(40,0.6,1.5))
def newobj(name,bm,m):
    me=bpy.data.meshes.new(name); bm.to_mesh(me); bm.free(); me.materials.append(m)
    for p in me.polygons: p.use_smooth=False
    return link(bpy.data.objects.new(name,me))
def tube(bm,pts,r,seg=8):
    # simple pipe along polyline
    rings=[]
    for i,p in enumerate(pts):
        d=(pts[min(i+1,len(pts)-1)]-pts[max(i-1,0)]).normalized()
        a=Vector((0,0,1)) if abs(d.z)<0.9 else Vector((1,0,0))
        u=d.cross(a).normalized(); v=d.cross(u)
        rings.append([bm.verts.new(p+r*(math.cos(2*math.pi*k/seg)*u+math.sin(2*math.pi*k/seg)*v)) for k in range(seg)])
    for a,b in zip(rings,rings[1:]):
        for k in range(seg): bm.faces.new((a[k],a[(k+1)%seg],b[(k+1)%seg],b[k]))
    bm.faces.new(rings[0][::-1]); bm.faces.new(rings[-1])
# ---------- 2. Kasser terrace steps (deck west edge), treads interpolate foot->deck per y ----------
Y0,Y1=-98.4,-77.6; XE=-199.0; N=5; TR=0.36; xf=XE-TR*N
ys=[Y0+i*0.5 for i in range(int((Y1-Y0)/0.5)+1)]
if ys[-1]<Y1-1e-3: ys.append(Y1)
zt_=[];zg_=[]
for y in ys:
    t=hit(XE+0.4,y,['COLE_plaza_deck_bs','COLE_plaza_edge_bs']); zt_.append(t[0] if t else None)
    g=hit(xf-0.6,y,['Terrain_LiDAR_DTM_1m']); zg_.append(g[0] if g else None)
def fill(a):
    v=[x for x in a if x is not None]; m=sum(v)/len(v); return [x if x is not None else m for x in a]
zt_=fill(zt_); zg_=fill(zg_)
sm=lambda a:[sum(a[max(0,i-2):i+3])/len(a[max(0,i-2):i+3]) for i in range(len(a))]
zt_=[t-0.01 for t in zt_]; zg_=sm(zg_)
risers=[(t-g)/N for t,g in zip(zt_,zg_)]
L('risers per y',[(round(y,1),round(r,3)) for y,r in zip(ys,risers)][::4])
ok=[r>=0.11 for r in risers]; run=(0,0,-1); i=0
while i<len(ok):
    if ok[i]:
        j=i
        while j+1<len(ok) and ok[j+1]: j+=1
        if j-i>run[2]-run[1]: run=(0,i,j)
        i=j+1
    else: i+=1
_,i0,i1=run; ys=ys[i0:i1+1]; zt_=zt_[i0:i1+1]; zg_=zg_[i0:i1+1]; risers=risers[i0:i1+1]; Y0,Y1=ys[0],ys[-1]
L('steps N',N,'riser min/max',round(min(risers),3),round(max(risers),3),'zt',round(min(zt_),2),round(max(zt_),2),'zg',round(min(zg_),2),round(max(zg_),2))
bm=bmesh.new(); prof=[]
for y,t,g in zip(ys,zt_,zg_):
    r=(t-g)/N; P=[(XE+0.3,g-0.4),(xf,g-0.4)]
    for i in range(N):
        x=xf+TR*i; z=g+r*(i+1); P+= [(x,z),(x+TR,z)]
    P+=[(XE+0.3,t)]
    prof.append([bm.verts.new((x,y,z)) for x,z in P])
for A,B in zip(prof,prof[1:]):
    n=len(A)
    for k in range(n): bm.faces.new((A[k],A[(k+1)%n],B[(k+1)%n],B[k]))
for E,sgn in ((prof[0],1),(prof[-1],-1)):
    try:
        f=bm.faces.new(E if sgn<0 else E[::-1])
    except Exception: pass
bmesh.ops.triangulate(bm,faces=[f for f in bm.faces if len(f.verts)>4],quad_method='BEAUTY',ngon_method='EAR_CLIP')
bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
st=newobj('WS35_Kasser_terrace_steps_concrete_5risers_UNVERIFIED',bm,M_conc)
# low concrete cheek walls at both ends, sloped with the flight
bm=bmesh.new()
for y,t,g,dy in ((ys[0],zt_[0],zg_[0],-0.15),(ys[-1],zt_[-1],zg_[-1],0.15)):
    pr=[(xf-0.15,g-0.4),(xf-0.15,g+0.2),(XE,t+0.12),(XE+0.3,t+0.12),(XE+0.3,g-0.4)]
    v0=[bm.verts.new((x,y+dy-0.15,z)) for x,z in pr]; v1=[bm.verts.new((x,y+dy+0.15,z)) for x,z in pr]
    n=len(pr)
    for k in range(n): bm.faces.new((v0[k],v0[(k+1)%n],v1[(k+1)%n],v1[k]))
    bm.faces.new(v0[::-1]); bm.faces.new(v1)
bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
newobj('WS35_Kasser_steps_cheek_walls_UNVERIFIED',bm,M_conc)
import bisect
def zat(y):
    i=min(range(len(ys)),key=lambda j:abs(ys[j]-y)); return zt_[i],zg_[i]
bm=bmesh.new()
for yr in (Y0+0.3,(Y0+Y1)/2,Y1-0.3):
    t,g=zat(yr); r=(t-g)/N
    tube(bm,[Vector((xf-0.3,yr,g-0.05)),Vector((xf-0.3,yr,g+0.9)),Vector((xf,yr,g+r+0.9)),Vector((XE,yr,t+0.9)),Vector((XE+0.5,yr,t+0.9)),Vector((XE+0.5,yr,t-0.05))],0.021)
    tube(bm,[Vector((xf-0.3,yr,g+0.45)),Vector((xf,yr,g+r+0.45)),Vector((XE,yr,t+0.45)),Vector((XE+0.5,yr,t+0.45))],0.015)
    for k in (2,4):
        x=xf+TR*k-TR/2; z=g+r*k
        tube(bm,[Vector((x,yr,z-0.05)),Vector((x,yr,z+0.9+r*0.5))],0.02)
newobj('WS35_Kasser_steps_pipe_handrails_slim_UNVERIFIED',bm,M_pipe)
ztop=sum(zt_)/len(zt_)
# ---------- 3. post-and-chain fence along the College Ave curb bed ----------
cl=bpy.data.objects['WS27_CollegeAve_curb_left_UNVERIFIED']
vs=[cl.matrix_world@v.co for v in cl.data.vertices]
COLE=Vector((-170,-95))
pts=[]
for yi in range(-150,-50):
    sl=[v for v in vs if abs(v.y-yi)<0.5]
    if not sl: continue
    v=max(sl,key=lambda v:v.x); pts.append(Vector((v.x,v.y)))
fence=[]; OFF=float(os.environ.get('FOFF','1.4'))
# resample at 2.1 m spacing along the polyline, offset toward Cole
acc=0; prev=None
for i,p in enumerate(pts):
    if prev is not None:
        acc+=(p-prev).length
    if prev is None or acc>=2.1:
        acc=0 if prev is not None else 0
        d=(pts[min(i+1,len(pts)-1)]-pts[max(i-1,0)]).normalized(); n=Vector((d.y,-d.x))
        if n.dot(COLE-p)<0: n=-n
        q=p+n*OFF
        fence.append(q)
    prev=p
posts=[]; REJ=[]
for q in fence:
    if Y0-1.0<q.y<Y1+1.0: posts.append(None); REJ.append('steps'); continue   # steps
    h=hit(q.x,q.y,ALL)
    if not h or h[1] in ('Footpaths_OSM','Roads_OSM','WS27_CollegeAve_carriageway_2020ortho','COLE_plaza_deck_bs','COLE_plaza_edge_bs','WS27_CollegeAve_curb_left_UNVERIFIED'): posts.append(None); REJ.append(h[1][:8] if h else 'none'); continue
    posts.append(Vector((q.x,q.y,h[0])))
from collections import Counter; L('rej',Counter(REJ)); L('fence candidates',len(fence),'posts',sum(1 for p in posts if p))
bm=bmesh.new(); bc=bmesh.new()
PH=0.75; CH=0.62
for i,p in enumerate(posts):
    if not p: continue
    tube(bm,[p-Vector((0,0,0.15)),p+Vector((0,0,PH))],0.035,10)
    bmesh.ops.create_uvsphere(bm,u_segments=10,v_segments=6,radius=0.048,matrix=Matrix.Translation(p+Vector((0,0,PH+0.02))))
    q=posts[i+1] if i+1<len(posts) else None
    if q and (q-p).length<3.2:
        a=p+Vector((0,0,CH)); b=q+Vector((0,0,CH)); cs=[]
        for k in range(13):
            t=k/12; z=-0.14*4*t*(1-t); cs.append(a.lerp(b,t)+Vector((0,0,z)))
        tube(bc,cs,0.009,6)
newobj('WS35_CollegeAve_bed_posts_black_PHOTO_JOE_20261110',bm,M_pipe)
newobj('WS35_CollegeAve_bed_chain_black_PHOTO_JOE_20261110',bc,M_pipe)
# ---------- 4. red hawk statue ----------
CROWNS=[(-205.1,-185.2,-125.7,-105.6),(-195.9,-184.7,-115.7,-103.1),(-191.9,-171.0,-140.0,-118.7)]
best=None
for gx in range(-193,-174):
    for gy in range(-132,-101):
        if any(x0-1.5<gx<x1+1.5 and y0-1.5<gy<y1+1.5 for x0,x1,y0,y1 in CROWNS): continue
        zs=[];bad=False
        for k in range(16):
            an=2*math.pi*k/16
            for rr in (1.2,2.4,3.0):
                h=hit(gx+rr*math.cos(an),gy+rr*math.sin(an),ALL)
                if not h or h[1]!='Terrain_LiDAR_DTM_1m': bad=True;break
                if rr<3: zs.append(h[0])
            if bad: break
        if bad: continue
        sl=max(zs)-min(zs)
        if best is None or sl<best[0]: best=(sl,gx,gy)
L('statue search best',best)
SX,SY=(float(os.environ['SX']),float(os.environ['SY'])) if 'SX' in os.environ else (best[1],best[2])
SZ=hit(SX,SY,['Terrain_LiDAR_DTM_1m'])[0]
W=Matrix.Translation((SX,SY,SZ))@Matrix.Rotation(math.radians(float(os.environ.get('SROT','10'))),4,'Z')
bm=bmesh.new(); bmesh.ops.create_circle(bm,cap_ends=True,segments=40,radius=2.4)
bmesh.ops.subdivide_edges(bm,edges=bm.edges[:],cuts=3,use_grid_fill=True)
bmesh.ops.triangulate(bm,faces=bm.faces[:])
for v in bm.verts:
    h=hit(SX+v.co.x,SY+v.co.y,['Terrain_LiDAR_DTM_1m']); v.co.z=(h[0] if h else SZ)-SZ+0.035
gmin=min(v.co.z for v in bm.verts)-0.035
o=newobj('WS35_RedHawk_mulch_ring_PHOTO_JOE',bm,M_mulch); o.matrix_world=Matrix.Translation((SX,SY,SZ))
bm=bmesh.new()
for k in range(14):
    a=2*math.pi*k/14+random.uniform(-0.05,0.05); r=random.uniform(0.32,0.42); bx,by=1.75*math.cos(a),1.75*math.sin(a)
    gz=hit(SX+bx,SY+by,['Terrain_LiDAR_DTM_1m'])[0]-SZ
    m=Matrix.Translation((bx,by,gz+r*0.6))@Matrix.Diagonal((r,r,r*0.85,1))
    bmesh.ops.create_icosphere(bm,subdivisions=3,radius=1,matrix=m)
for v in bm.verts:
    v.co+=v.normal*random.uniform(-0.04,0.04)
o=newobj('WS35_RedHawk_boxwood_ring_PHOTO_JOE',bm,M_box); o.matrix_world=Matrix.Translation((SX,SY,SZ))
for p in o.data.polygons: p.use_smooth=True
# plinth
bm=bmesh.new(); bmesh.ops.create_cone(bm,cap_ends=True,segments=32,radius1=0.85,radius2=0.82,depth=0.56-gmin+0.25,matrix=Matrix.Translation((0,0,(0.56+gmin-0.25)/2)))
for v in bm.verts:
    if v.co.z>0.5: v.co.z+=random.uniform(-0.03,0.03); v.co.x*=random.uniform(0.98,1.02)
o=newobj('WS35_RedHawk_plinth_granite_PHOTO_JOE',bm,M_gran); o.matrix_world=W
bv=o.modifiers.new('bevel','BEVEL'); bv.width=0.03; bv.segments=2
# bronze sculpture: rock + hawk
bm=bmesh.new()
bmesh.ops.create_icosphere(bm,subdivisions=3,radius=1,matrix=Matrix.Translation((0,0.05,0.62))@Matrix.Diagonal((0.6,0.5,0.32,1)))
for v in bm.verts:
    if v.co.z>0.6: v.co+=v.normal*random.uniform(-0.06,0.07)
    else: v.co.z=max(v.co.z,0.55)
RT=0.88  # rock top
def ell(c,s,rot=Matrix.Identity(4),sub=3):
    bmesh.ops.create_icosphere(bm,subdivisions=sub,radius=1,matrix=Matrix.Translation(c)@rot@Matrix.Diagonal((*s,1)))
fw=Matrix.Rotation(math.radians(-38),4,'X')  # lean forward (+Y)
ell((0,0.14,1.72),(0.24,0.26,0.55),fw)                 # body
ell((0,0.36,2.12),(0.19,0.22,0.27),fw)                 # chest/neck
ell((0,0.50,2.36),(0.13,0.19,0.13))                     # head
bmesh.ops.create_cone(bm,cap_ends=True,segments=8,radius1=0.07,radius2=0.004,depth=0.22,matrix=Matrix.Translation((0,0.72,2.31))@Matrix.Rotation(math.radians(-120),4,'X'))  # beak
for sx in (-1,1):
    ell((sx*0.13,0.16,1.36),(0.11,0.13,0.22),fw)             # thigh feathers
    tube(bm,[Vector((sx*0.15,0.14,1.2)),Vector((sx*0.13,0.2,RT+0.12))],0.045,8)  # legs
    for a in (-30,0,30):
        d=Matrix.Rotation(math.radians(a),3,'Z')@Vector((0,0.18,0))
        base=Vector((sx*0.13,0.2,RT+0.06)); tube(bm,[base,base+d,base+d*1.25-Vector((0,0,0.06))],0.022,6)
    tube(bm,[Vector((sx*0.13,0.2,RT+0.06)),Vector((sx*0.13,0.04,RT+0.02))],0.02,6)
def feather(origin,dirv,nrm,Lg,wd,th=0.025):
    side=dirv.cross(nrm).normalized(); ps=[]
    for k in range(7):
        t=k/6; w=wd*(0.55+0.45*math.sin(math.pi*min(1,t*1.15)))*(1-t**4*0.85)
        ps.append((origin+dirv*Lg*t+nrm*0.03*math.sin(math.pi*t),w))
    vs=[]
    for c,w in ps:
        vs.append([bm.verts.new(c+side*w/2+nrm*th/2),bm.verts.new(c-side*w/2+nrm*th/2),bm.verts.new(c-side*w/2-nrm*th/2),bm.verts.new(c+side*w/2-nrm*th/2)])
    for a,b in zip(vs,vs[1:]):
        for k in range(4): bm.faces.new((a[k],a[(k+1)%4],b[(k+1)%4],b[k]))
    bm.faces.new(vs[0][::-1]); bm.faces.new(vs[-1])
for sx in (-1,1):
    sh=Vector((sx*0.22,0.05,2.15))
    S=Vector((sx*1.0,-0.05,0.8)).normalized()          # span: up and out
    C=Vector((0,-1,-0.15)); C=(C-S*C.dot(S)).normalized()  # chord: back
    Nw=S.cross(C).normalized()
    if Nw.y<0: Nw=-Nw
    wr=sh+S*0.9
    tube(bm,[sh,sh+S*0.4+Nw*0.04,wr],0.07,8)               # arm leading edge
    for k in range(9):                                   # primaries fanned from wrist
        a=math.radians(8+k*9.5); d=(S*math.cos(a)+C*math.sin(a)).normalized()
        feather(wr-Nw*0.01*k,d,Nw,1.2-0.05*k,0.19)
    for k in range(9):                                   # secondaries along arm
        t=k/8; o=sh.lerp(wr,0.15+0.85*t); d=(C*0.92+S*0.25*(1-t)).normalized()
        feather(o-Nw*0.02,d,Nw,0.7,0.2)
    for k in range(10):                                  # coverts
        t=k/9; o=sh.lerp(wr,0.05+0.9*t)+C*0.05; d=(C*0.95+S*0.2).normalized()
        feather(o+Nw*0.03,d,Nw,0.38,0.16)
for k in range(7):                                       # tail fan
    a=math.radians(-30+k*10); d=(Matrix.Rotation(a,3,'Y')@Vector((0,-0.55,-0.8))).normalized()
    feather(Vector((0,-0.12,1.32)),d,Vector((0,0.82,-0.55)).normalized(),0.62,0.13)
o=newobj('WS35_RedHawk_statue_bronze_PHOTO_JOE_20261110_pos_UNVERIFIED',bm,M_bronze); o.matrix_world=W
o.modifiers.new('ws','WEIGHTED_NORMAL')
for p in o.data.polygons: p.use_smooth=True
L('statue verts',len(o.data.vertices))
# ---------- cameras ----------
ter=bpy.data.objects['Terrain_LiDAR_DTM_1m']
def cam(n,loc,tgt,lens,eye=None):
    if eye is not None:
        h=hit(loc[0],loc[1],['Terrain_LiDAR_DTM_1m','Footpaths_OSM','WS27_CollegeAve_carriageway_2020ortho']); loc=(loc[0],loc[1],h[0]+eye)
    c=bpy.data.objects.get(n)
    if not c:
        c=bpy.data.objects.new(n,bpy.data.cameras.new(n)); sc.collection.objects.link(c)
    c.location=loc; c.data.lens=lens; c.data.clip_start=0.1; c.data.clip_end=3000
    c.rotation_euler=(Vector(tgt)-Vector(loc)).to_track_quat('-Z','Y').to_euler(); return c
cam('WS35_CAM_oblique_Kasser_Cole_frontage_from_SW',(-240,-150,152),(-192,-95,128),26)
cam('WS35_CAM_eye_Kasser_steps_from_CollegeAve_SW',(-214,-104,0),(-200,-86,ztop+0.3),26,1.6)
cam('WS35_CAM_eye_RedHawk_statue_match4_from_W',(SX-12,SY+1.5,0),(SX,SY,SZ+1.8),30,1.6)
cam('WS35_CAM_closeup_RedHawk_statue',(SX-4.2,SY+3.2,0),(SX,SY,SZ+2.0),32,1.4)
open('/workspace/nj-scenes/montclair-state/scripts/ws35/build_log.txt','w').write('\n'.join(log))
if os.environ.get('SAVE')=='1':
    bpy.ops.wm.save_mainfile(); print('SAVED',flush=True)
