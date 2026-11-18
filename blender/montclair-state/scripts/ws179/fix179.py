# ws179 DRAFT (NOT YET RUN — subset-test first, see prep/ws179_mulch/REFS.md): UNIFY #87 — College Avenue continues SOUTH of Normal Ave.
# The "dark driveway/apron at t 6-14" on the WS110 S side is the College Ave S leg (OSM 232846669 highway=service name=College Avenue,
# continuing as 11620853 residential): 2017 + 2023 LiDAR class-2 asphalt (1.5-3k) from the gutter to beyond s -26 at t 5.25..13.25,
# interrupting the S sidewalk (bright 9-12k elsewhere) at t ~4.8..15.8 (curb returns); E edge has a 14-18 cm curb step, W edge only 4-6 cm.
# OSM 1504781938 = marked crosswalk (crossing:markings=lines) along the S walk line across the leg mouth.
# Design (ws173 road frame A=(-268.8,-262.9), s north+, t east+; WS110 S curb face s_f(t) = -0.01446 t - 10.278 after #80):
#   - delete WS110 S curb / S walk / WS175 walk-back lip / WS113 proxy faces whose centroid is inside the new asphalt footprint
#   - new WS179 carriageway: leg W edge 5.75 (-> 4.85 at s -26), E edge 13.25; returns R_W 2.5 (tangent t 2.75), R_E 5.5 (tangent t 18.75),
#     z = WS110 carriageway top at the gutter row blended over 3 m into the 2023 DTM (prep/ws179_mulch/dtm179.npy, ~117.9 flat), stub to s -26
#   - curbs on both returns + leg edges: E/E-return reveal 0.15 (LiDAR), W/W-return reveal 0.05 (LiDAR 4-6 cm; low/rolled curb UNVERIFIED);
#     reveal eased to 0.015 where a return crosses the walk band (curb-ramp landings for the crosswalk)
#   - walk ends ramped: WS110 S walk verts within 1.5 m of a return are lowered toward the ramp landing (front edge -> road+0.015)
#   - crosswalk: two 0.30 m white lines centred at s_f-0.75 and s_f-2.95 between the returns (2023 LiDAR intensity bands, not in 2017; OSM lines;
#     line width 0.30 UNVERIFIED — LiDAR bands read ~0.4-0.6 m incl. footprint blur)
#   - ground/lawn verts under the new footprint pushed to paving-0.05 (fix178 rule)
# Env: DRY=1 -> report counts only (no edits).
import bpy, bmesh, math, os, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
OB=bpy.data.objects; DRY=os.environ.get('DRY')=='1'
A=np.array([-268.8,-262.9]); N=np.array([0.236,1.0]); N/=np.linalg.norm(N); T=np.array([N[1],-N[0]])
def st(x,y): d=np.array((x,y))-A; return float(d@N), float(d@T)
def xy(s,t): p=A+N*s+T*t; return float(p[0]),float(p[1])
def sf(t): return -0.01446*t-10.278
RW,RE=2.5,5.5; S_END=-26.0
def wedge(s): return 5.75 if s>=-19 else 5.75+(4.85-5.75)*(-19-s)/7.0   # LiDAR single-return asphalt edge (footprint179_check.out)
EEDGE=13.25
TW=wedge(sf(3)-RW)-RW; TE=EEDGE+RE          # tangent points on the face line
def inside(s,t,pad=0.0):
    """True if (s,t) is in the new asphalt footprint (S of the face line)."""
    f=sf(t)
    if s>f+pad or s<S_END-pad: return False
    cw=(wedge(s)-RW, f-RW); ce=(EEDGE+RE, f-RE)
    if t<TW-pad or t>TE+pad: return False
    if t<wedge(s)-pad:      # W corner zone
        return s>cw[1] and math.hypot(t-cw[0],s-cw[1])>RW-pad
    if t>EEDGE+pad:         # E corner zone
        return s>ce[1] and math.hypot(t-ce[0],s-ce[1])>RE-pad
    return True
D=np.load('/workspace/nj-scenes/montclair-state/prep/ws179_mulch/dtm179.npy')[0]; X0,Y0,R=-315.0,-295.0,0.5
def dtm(x,y):
    fi=(x-X0)/R-0.5; fj=(y-Y0)/R-0.5
    i=int(min(max(math.floor(fi),0),D.shape[1]-2)); j=int(min(max(math.floor(fj),0),D.shape[0]-2)); tx=min(max(fi-i,0),1); ty=min(max(fj-j,0),1)
    return float(D[j,i]*(1-tx)*(1-ty)+D[j,i+1]*tx*(1-ty)+D[j+1,i]*(1-tx)*ty+D[j+1,i+1]*tx*ty)
def obs(pfx): return [o for o in OB if o.type=='MESH' and o.name.startswith(pfx)]
dg=bpy.context.evaluated_depsgraph_get()
def bvh(objs):
    out=[]
    for o in objs:
        oe=o.evaluated_get(dg); m=oe.to_mesh(); m.transform(o.matrix_world)
        out.append(BVHTree.FromPolygons([v.co.copy() for v in m.vertices],[tuple(p.vertices) for p in m.polygons])); oe.to_mesh_clear()
    return out
def top(trees,x,y):
    z=None
    for b in trees:
        h=b.ray_cast(Vector((x,y,200)),Vector((0,0,-1)),300)
        if h[0] is not None and (z is None or h[0].z>z): z=h[0].z
    return z
ROAD=bvh(obs('WS110_NormalAve_carriageway_W11p3'))
def zroad(s,t):
    """gutter z from the WS110 carriageway at the face, blended into DTM over 3 m south of the face"""
    f=sf(t); xg,yg=xy(f+0.25,min(max(t,TW),TE)); zg=top(ROAD,xg,yg)
    x,y=xy(s,t); zd=dtm(x,y)
    if zg is None: return zd
    u=min(max((f-s)/3.0,0.0),1.0); u=u*u*(3-2*u)
    return zg+(zd-zg)*u
# ---------- 1. delete old S-side paving faces inside the footprint ----------
DEL=('WS110_NormalAve_curb_W11p3','WS110_NormalAve_sidewalk_ws85','WS175_WS110_walk_back_lawn_lip_S','WS113_paving_tops_proxy')
for p in DEL:
    for o in obs(p):
        mw=o.matrix_world; bm=bmesh.new(); bm.from_mesh(o.data); kill=[]
        for fc in bm.faces:
            c=mw@fc.calc_center_median(); s,t=st(c.x,c.y)
            if s<-5 and inside(s,t,pad=0.02): kill.append(fc)
        print('FIX179 del',o.name[:60],len(kill),'of',len(bm.faces),flush=True)
        if not DRY and kill: bmesh.ops.delete(bm,geom=kill,context='FACES'); bm.to_mesh(o.data); o.data.update()
        bm.free()
# ---------- 2. ramp the S walk ends toward the returns ----------
WALK=obs('WS110_NormalAve_sidewalk_ws85'); nr=0
for o in WALK:
    mw=o.matrix_world; mi=mw.inverted()
    for v in o.data.vertices:
        w=mw@v.co; s,t=st(w.x,w.y)
        if not (sf(t)-2.1<s<sf(t)+0.05): continue
        d=min(abs(t-TW),abs(t-TE)) if (t<TW or t>TE) else 0.0
        if d>1.5: continue
        u=1-d/1.5; zt=zroad(sf(t)-0.5,min(max(t,TW),TE))+0.015
        nz=w.z+(min(w.z,zt+0.06*(1-u))-w.z)*u
        if not DRY: w.z=nz; v.co=mi@w
        nr+=1
    if not DRY: o.data.update()
print('FIX179 walk verts ramped',nr,flush=True)
if DRY: print('FIX179 DRY done',flush=True); raise SystemExit
# ---------- 3. carriageway grid (0.25 m) clipped to the footprint ----------
def getmat(name,col,rough=0.9):
    m=bpy.data.materials.get(name)
    if m: return m
    m=bpy.data.materials.new(name); m.use_nodes=True; b=m.node_tree.nodes['Principled BSDF']; b.inputs['Base Color'].default_value=col; b.inputs['Roughness'].default_value=rough; return m
ref=obs('WS110_NormalAve_carriageway_W11p3'); asph=ref[0].active_material if ref and ref[0].active_material else getmat('WS179_asphalt',(0.11,0.11,0.105,1))
cref=obs('WS110_NormalAve_curb_W11p3'); conc=cref[0].active_material if cref and cref[0].active_material else getmat('WS179_concrete',(0.5,0.49,0.46,1))
paint=getmat('WS179_crosswalk_paint_white',(0.8,0.8,0.78,1),0.6)
col=bpy.data.collections.get('WS179_CollegeAve_S_leg') or bpy.data.collections.new('WS179_CollegeAve_S_leg')
if col.name not in bpy.context.scene.collection.children: bpy.context.scene.collection.children.link(col)
for o in [o for o in OB if o.name.startswith('WS179_')]: OB.remove(o)
def link(nm,bm,mat):
    me=bpy.data.meshes.new(nm); bm.to_mesh(me); bm.free(); me.materials.append(mat); o=OB.new(nm,me); col.objects.link(o); return o
G=0.25; ts=np.arange(TW-0.5,TE+0.5+1e-6,G); ss=np.arange(sf(TE)+0.3,S_END-1e-6,-G)
bm=bmesh.new(); V={}
for i,s in enumerate(ss):
    for j,t in enumerate(ts):
        x,y=xy(s,t); V[i,j]=bm.verts.new((x,y,zroad(s,t)+0.004))
nf=0
for i in range(len(ss)-1):
    for j in range(len(ts)-1):
        c=(0.5*(ss[i]+ss[i+1]),0.5*(ts[j]+ts[j+1]))
        if inside(*c): bm.faces.new((V[i,j],V[i,j+1],V[i+1,j+1],V[i+1,j])); nf+=1
for v in [v for v in bm.verts if not v.link_faces]: bm.verts.remove(v)
car=link('WS179_CollegeAve_S_leg_carriageway_OSM232846669_LiDAR2023_UNVERIFIEDreturns',bm,asph); print('FIX179 carriageway faces',nf,flush=True)
# ---------- 4. curbs along the footprint edge (W return + W edge, E return + E edge) ----------
def edge_pts(side):
    pts=[]
    if side=='W':
        cs=sf(TW)-RW
        for k in range(13):
            a=math.pi/2*k/12; t=(TW)+RW*math.sin(a); s=sf(t)-RW*(1-math.cos(a)); pts.append((s,t))
        for s in np.arange(pts[-1][0]-0.5,S_END-1e-6,-0.5): pts.append((s,wedge(s)))
    else:
        for k in range(17):
            a=math.pi/2*k/16; t=TE-RE*math.sin(a); s=sf(t)-RE*(1-math.cos(a)); pts.append((s,t))
        for s in np.arange(pts[-1][0]-0.5,S_END-1e-6,-0.5): pts.append((s,EEDGE))
    return pts
for side,rev,outdir in (('W',0.05,-1),('E',0.15,+1)):
    P=edge_pts(side); bm=bmesh.new(); rows=[]
    for s,t in P:
        f=sf(t); inwalk=(f-2.1<s<f-0.15)
        r=0.015 if inwalk else rev
        zr=zroad(s,t)+0.004; xa,ya=xy(s,t); xb,yb=xy(s,t+outdir*0.15)
        rows.append([bm.verts.new((xa,ya,zr-0.10)),bm.verts.new((xa,ya,zr+r)),bm.verts.new((xb,yb,zr+r)),bm.verts.new((xb,yb,zr-0.10))])
    for a,b in zip(rows[:-1],rows[1:]):
        for k in range(3): bm.faces.new((a[k],a[k+1],b[k+1],b[k]))
    bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
    link('WS179_CollegeAve_S_leg_curb_%s_reveal%dcm_LiDAR2023_UNVERIFIED'%(side,round(rev*100)),bm,conc)
print('FIX179 curbs built',flush=True)
# ---------- 5. crosswalk lines (OSM crossing:markings=lines) ----------
for k,off in enumerate((0.75,2.95)):   # 2023 LiDAR bright bands at face offset -0.5..-1.0 and -2.6..-3.25 (prep/ws179_mulch/xwalk179.out); absent in 2017
    bm=bmesh.new(); row=[]
    for t in np.arange(TW+0.3,TE-0.3+1e-6,0.25):
        f=sf(t); s0=f-off+0.15; s1=f-off-0.15
        if not (inside(s0,t) and inside(s1,t)): continue
        a=xy(s0,t); b=xy(s1,t); row.append((bm.verts.new((a[0],a[1],zroad(s0,t)+0.009)),bm.verts.new((b[0],b[1],zroad(s1,t)+0.009))))
    for (a0,a1),(b0,b1) in zip(row[:-1],row[1:]): bm.faces.new((a0,a1,b1,b0))
    link('WS179_CollegeAve_S_leg_crosswalk_line%d_OSM1504781938_UNVERIFIEDspacing'%k,bm,paint)
# ---------- 6. ground under the footprint ----------
CAR=bvh([car]); ng=0
for p in ('WS110_ground_patch','WS175_WS110_walk_back_lawn_lip_S','WS163_ground_patch_W','WS172_frontyards','WS163_walk_back_lawn_lip_S'):
    for o in obs(p):
        mw=o.matrix_world; mi=mw.inverted(); k=0
        for v in o.data.vertices:
            w=mw@v.co; s,t=st(w.x,w.y)
            if not inside(s,t,pad=0.4): continue
            zt=top(CAR,w.x,w.y)
            if zt is None: zt=zroad(s,t)
            if w.z>zt-0.05: w.z=zt-0.05; v.co=mi@w; k+=1
        o.data.update(); ng+=k
        if k: print('FIX179 ground',o.name[:60],k,flush=True)
print('FIX179 done ground',ng,flush=True)
