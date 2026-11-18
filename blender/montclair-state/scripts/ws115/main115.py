# ws115: UNIFY #16 - clean designed concrete walk on OSM 312849086 (last leg) from the brick link N end to the plaza at y~-202; retire crumpled Footpaths/OZ joints in its footprint
import bpy, bmesh, numpy as np, os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R='/workspace/nj-scenes/montclair-state/'
DT=np.load(R+'data/dtm_1m.npy'); H=DT.shape[0]/2
def dtm(x,y):
    fx=x+H-0.5; fy=y+H-0.5; j=int(np.floor(fx)); i=int(np.floor(fy)); a=fx-j; b=fy-i
    return float(DT[i,j]*(1-a)*(1-b)+DT[i,j+1]*a*(1-b)+DT[i+1,j]*(1-a)*b+DT[i+1,j+1]*a*b)
O=lambda p: next(o for o in bpy.data.objects if o.name.startswith(p))
A=np.array([-235.4,-235.3]);B=np.array([-222.0,-197.4]);L=float(np.linalg.norm(B-A));d=(B-A)/L;n=np.array([-d[1],d[0]])
def st(x,y): q=np.array([x,y])-A; return float(q@d),float(q@n)
def W(s,t): p=A+d*s+n*t; return float(p[0]),float(p[1])
S1=34.6; HW=1.0
dg=bpy.context.evaluated_depsgraph_get()
# --- evaluated probe of paving near the top end + Footpaths in footprint
def evtops(ob):
    e=ob.evaluated_get(dg); me=e.to_mesh(); mw=ob.matrix_world
    vs=[tuple(mw@v.co) for v in me.vertices]; ps=[tuple(p.vertices) for p in me.polygons if p.normal.z>0.5]
    e.to_mesh_clear(); return BVHTree.FromPolygons(vs,ps) if ps else None
fp=O('Footpaths_OSM'); bfp=evtops(fp)
def zr(b,x,y):
    h=b.ray_cast(Vector((x,y,200)),Vector((0,0,-1)),150); return None if h[0] is None else h[0].z
for s in np.arange(0,40,2.0):
    x,y=W(s,0); print('M115 fp eval s%4.1f'%s,'dtm %.2f'%dtm(x,y),'fp',None if zr(bfp,x,y) is None else round(zr(bfp,x,y)-dtm(x,y),2))
# --- retire Footpaths / OZ joint faces inside the footprint (base mesh)
def inside(x,y,buf):
    s,t=st(x,y); return -0.3<=s<=S1+0.2 and abs(t)<=HW+buf
tot={}
for ob in list(bpy.data.objects):
    if ob.type!='MESH': continue
    if not (ob.name.startswith('Footpaths_OSM') or ob.name.startswith('OZ_')): continue
    bb=[ob.matrix_world@Vector(c) for c in ob.bound_box]
    if max(v.x for v in bb)<-238 or min(v.x for v in bb)>-220 or max(v.y for v in bb)<-237 or min(v.y for v in bb)>-196: continue
    mw=ob.matrix_world; bm=bmesh.new(); bm.from_mesh(ob.data)
    kill=[f for f in bm.faces if inside(*(mw@f.calc_center_median())[:2],0.35)]
    if kill:
        bmesh.ops.delete(bm,geom=kill,context='FACES'); bm.to_mesh(ob.data); ob.data.update(); tot[ob.name[:40]]=len(kill)
    bm.free()
print('M115 retired',tot)
# --- profile
bl=O('WS112_CollegeAve_S_E_walk_N_brick'); V=bl.data.vertices; mwb=bl.matrix_world
last=np.array([tuple(mwb@V[i].co) for i in range(115,120)])
z0=float(last[2,2]); s0,_=st(*last[2,:2])
ss=np.r_[np.arange(0,S1,0.5),S1]
dc=np.array([dtm(*W(s,0)) for s in ss]); p=np.polyfit(ss,dc,3); fit=np.polyval(p,ss)+0.05
# top end: evaluated paving there?
xe,ye=W(S1+0.6,0); ze=zr(bfp,xe,ye); print('M115 end paving z',ze,'dtm',dtm(xe,ye),'fit end',fit[-1])
u=np.clip(ss/8.0,0,1); u=u*u*(3-2*u); zc=fit+(z0-fit[0])*(1-u)
if ze is not None and abs(ze-dtm(xe,ye))<0.35:
    v=np.clip((ss-(S1-3))/3.0,0,1); v=v*v*(3-2*v); zc=zc*(1-v)+(ze+0.005)*v
g=np.diff(zc)/np.diff(ss); print('M115 grade%% min %.2f max %.2f'%(100*g.min(),100*g.max()),'z',zc[0].round(3),zc[-1].round(3))
rows=[]
for k,s in enumerate(ss):
    u2=min(s/2.0,1.0); u2=u2*u2*(3-2*u2)
    r=[]
    for j,f in enumerate(np.linspace(0,1,5)):
        t=HW-2*HW*f   # W(+)..E(-)
        x,y=W(s,t); zz=zc[k]-0.015*t
        if u2<1:
            lp=last[4-j] if st(*last[0,:2])[1]<st(*last[4,:2])[1] else last[j]
            x=lp[0]*(1-u2)+x*u2; y=lp[1]*(1-u2)+y*u2; zz=lp[2]*(1-u2)+zz*u2
        r.append((x,y,zz))
    rows.append(r)
mc=O('WS111_CollegeAve_S_E_walk_gap').active_material
col=bpy.data.collections.new('WS115_E_walk_N_to_plaza'); bpy.context.scene.collection.children.link(col)
bm=bmesh.new(); T=[[bm.verts.new(q) for q in r] for r in rows]
Lw=[bm.verts.new((r[0][0],r[0][1],r[0][2]-0.3)) for r in rows]; Rw=[bm.verts.new((r[-1][0],r[-1][1],r[-1][2]-0.3)) for r in rows]
for i in range(len(rows)-1):
    for j in range(4): bm.faces.new((T[i][j],T[i][j+1],T[i+1][j+1],T[i+1][j]))
    bm.faces.new((Lw[i],T[i][0],T[i+1][0],Lw[i+1])); bm.faces.new((T[i][-1],Rw[i],Rw[i+1],T[i+1][-1]))
bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
if sum(f.normal.z for f in bm.faces if abs(f.normal.z)>0.5)<0: bmesh.ops.reverse_faces(bm,faces=bm.faces)
me=bpy.data.meshes.new('WS115_E_walk_N_concrete_OSM312849086_ortho2020_2m_UNVERIFIEDw'); bm.to_mesh(me); bm.free(); me.materials.append(mc)
for pl in me.polygons: pl.use_smooth=False
wk=bpy.data.objects.new(me.name,me); col.objects.link(wk)
print('M115 walk faces',len(me.polygons),'mat',mc.name if mc else None)
# --- fin: base Terrain verts ~1 m above the 2023 DTM/class-2 points between the walk and Chapin (no ground there) -> snap to DTM
to=O('Terrain_LiDAR_DTM_1m'); mw=to.matrix_world; inv=mw.inverted(); nf=0; mxf=0
for v in to.data.vertices:
    w=mw@v.co
    if -236<w.x<-212 and -234<w.y<-200:
        dz=w.z-dtm(w.x,w.y)
        if dz>0.15: mxf=max(mxf,dz); w.z=dtm(w.x,w.y)-0.01; v.co=inv@w; nf+=1
to.data.update(); print('M115 fin snapped',nf,'max dz %.2f'%mxf)
# --- lawn: lift near edges, push down under the walk
tops=[];planes=[]
for f in me.polygons:
    if f.normal.z<0.7: continue
    vs=[me.vertices[i].co.copy() for i in f.vertices]; tops.append([Vector((v.x,v.y,0)) for v in vs]); planes.append((vs[0],f.normal.copy()))
vv=[];pp=[]
for t in tops: b=len(vv); vv+=t; pp.append(list(range(b,b+len(t))))
bvh=BVHTree.FromPolygons(vv,pp)
def zat(i,x,y): p0,nn=planes[i]; return p0.z-(nn.x*(x-p0.x)+nn.y*(y-p0.y))/nn.z
for pn in ('WS113_terrain_fan_fill','WS110_ground_patch','Terrain_LiDAR_DTM_1m'):
    try: o=O(pn)
    except StopIteration: continue
    m2=o.data; mw=o.matrix_world; inv=mw.inverted(); nl=nd=0; mx=0
    for v in m2.vertices:
        w=mw@v.co
        if not (-240<w.x<-218 and -238<w.y<-194): continue
        loc,nor,idx,dd=bvh.find_nearest(Vector((w.x,w.y,0)),1.3)
        if loc is None: continue
        ze2=zat(idx,loc.x,loc.y)
        if dd<0.02:
            if w.z>ze2-0.06: w.z=ze2-0.06; v.co=inv@w; nd+=1
        else:
            tgt=ze2-0.03-0.12*dd
            if w.z<tgt and tgt-w.z<0.5: mx=max(mx,tgt-w.z); w.z=tgt; v.co=inv@w; nl+=1
    m2.update(); print('M115 lawn',o.name[:30],'lift',nl,'max %.3f'%mx,'down',nd)
# --- proxy append
pv=bpy.data.objects.get('WS113_paving_tops_proxy')
if pv:
    b2=bmesh.new(); b2.from_mesh(pv.data); n0=len(b2.faces)
    t=bmesh.new(); t.from_mesh(me); t.normal_update(); bmesh.ops.delete(t,geom=[f for f in t.faces if f.normal.z<0.5],context='FACES')
    m3=bpy.data.meshes.new('tmp'); t.to_mesh(m3); t.free(); b2.from_mesh(m3); bpy.data.meshes.remove(m3)
    b2.to_mesh(pv.data); b2.free(); pv.data.update(); print('M115 proxy',n0,'->',len(pv.data.polygons))
SAVE=os.environ.get('SAVE','main')
if SAVE=='main': bpy.ops.wm.save_mainfile(); print('M115 SAVED main')
else: bpy.ops.wm.save_as_mainfile(filepath=SAVE,copy=True); print('M115 SAVED',SAVE)
