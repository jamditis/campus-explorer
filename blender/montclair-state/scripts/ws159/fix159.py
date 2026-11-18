# ws159: UNIFY #63 — Panzer front: clip draped old walk/joint/helper pieces, build lower front walk, wing-front + bank mulch beds, steps, lanterns, downspouts
import bpy, bmesh, math, numpy as np
from mathutils import Vector
M='/workspace/nj-scenes/montclair-state/'
th=math.radians(76.8); A=Vector((math.cos(th),math.sin(th),0)); B=Vector((math.cos(th-math.pi/2),math.sin(th-math.pi/2),0)); O=Vector((-238.1,-180.2,0))
def P(a,b,z): return O+A*a+B*b+Vector((0,0,z))
def AB(v): w=Vector((v.x,v.y,0))-O; return w.dot(A), w.dot(B)
# --- LiDAR ground grid (class 2) for the bank ---
d=np.load(M+'data/pts_panzer158.npz'); X,Y,Z,C=d['x'],d['y'],d['z'],d['c']
g=C==2; X,Y,Z=X[g],Y[g],Z[g]; ga=(X-O.x)*A.x+(Y-O.y)*A.y; gb=(X-O.x)*B.x+(Y-O.y)*B.y
def gz(a,b,r=0.6):
    m=(abs(ga-a)<r)&(abs(gb-b)<r)
    if m.sum()<3: m=(abs(ga-a)<1.2)&(abs(gb-b)<1.2)
    return float(np.median(Z[m])) if m.sum()>=3 else None
# --- 1. clip ---
ZONE=(-6.0,25.0,-2.5,8.6); WALK_B=(0.0,3.2)
def inzone(a,b): return ZONE[0]<=a<=ZONE[1] and ZONE[2]<=b<=ZONE[3]
tot=0
for ob in list(bpy.data.objects):
    if ob.type!='MESH': continue
    n=ob.name; nl=n.lower()
    if n.startswith(('WS158','WS159')): continue
    hit=n.startswith('OZ_walk_joints') or n.startswith('WS86_grandstand_DTM_target') or n=='WS105_PanzerE_lower_walkway' or ('footpath' in nl) or ('walk_joint' in nl)
    if not hit: continue
    mw=ob.matrix_world; me=ob.data
    cand=[p.index for p in me.polygons if inzone(*AB(mw@p.center))]
    if not cand: continue
    if me.users>1: ob.data=me.copy(); me=ob.data
    bm=bmesh.new(); bm.from_mesh(me); bm.faces.ensure_lookup_table()
    fs=[bm.faces[i] for i in cand]
    bmesh.ops.delete(bm,geom=fs,context='FACES'); bm.to_mesh(me); bm.free(); tot+=len(cand)
    print('FIX159 clip',n,len(cand),'mods',[m.type for m in ob.modifiers])
print('FIX159 clipped faces',tot)
# --- materials / helpers ---
col=bpy.data.collections.new('WS159_Panzer_front_walk_beds'); bpy.context.scene.collection.children.link(col)
def mat(n,rgb,rough=0.6,metal=0.0):
    m=bpy.data.materials.get(n) or bpy.data.materials.new(n); m.use_nodes=True
    b=m.node_tree.nodes.get('Principled BSDF'); b.inputs['Base Color'].default_value=(*rgb,1); b.inputs['Roughness'].default_value=rough; b.inputs['Metallic'].default_value=metal; return m
CON=mat('WS159_concrete_walk_broomed',(0.58,0.57,0.54),0.85)
MUL=mat('WS159_mulch_dark_shredded',(0.11,0.065,0.04),0.95)
EDG=mat('WS159_bed_edge_concrete_curb',(0.62,0.61,0.58),0.8)
BLK=mat('WS159_lantern_black_metal',(0.02,0.02,0.02),0.4,0.6)
LGL=mat('WS159_lantern_glass_frosted',(0.85,0.82,0.7),0.3)
DSP=bpy.data.materials.get('WS158_fascia_redbrown') or mat('WS159_downspout_redbrown',(0.30,0.07,0.05),0.5)
def obj(name,verts,faces,mats,mi=None):
    me=bpy.data.meshes.new(name); me.from_pydata([tuple(v) for v in verts],[],faces)
    for m in mats: me.materials.append(m)
    if mi:
        for p,k in zip(me.polygons,mi): p.material_index=k
    bm=bmesh.new(); bm.from_mesh(me); bmesh.ops.remove_doubles(bm,verts=bm.verts,dist=0.002); bmesh.ops.recalc_face_normals(bm,faces=bm.faces); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth=False
    o=bpy.data.objects.new(name,me); col.objects.link(o); return o
def slab(a0,a1,b0,b1,ztop,th=0.15):
    c=[P(a0,b0,0),P(a1,b0,0),P(a1,b1,0),P(a0,b1,0)]; V=[p+Vector((0,0,ztop)) for p in c]+[p+Vector((0,0,ztop-th)) for p in c]
    F=[[0,1,2,3],[7,6,5,4],[0,4,5,1],[1,5,6,2],[2,6,7,3],[3,7,4,0]]; return V,F
def merge(parts):
    V=[];F=[]
    for v,f in parts:
        o=len(V); V+=v; F+=[[i+o for i in q] for q in f]
    return V,F
# --- 2. lower front walk (OSM 312847980 centreline b 1.1-1.8; LiDAR flat 122.22-122.31 b 0..4.5) ---
ZW=122.31
w=[slab(-5.0,25.0,0.0,3.2,ZW)]
# door spur to the centre storefront is inside the walk; S wing / N wing front strips are beds
obj('WS159_PanzerE_front_walk_concrete_LiDAR_OSM',*merge(w),[CON])
# --- 3. wing-front mulch beds (cch_1: planting tight to the S wing wall) b -1.8..0 with 0.15 m concrete edge on the walk side ---
beds=[slab(-4.9,0.0,-1.8,-0.12,ZW-0.04,0.2),slab(18.3,24.0,-1.7,-0.12,ZW-0.04,0.2)]
obj('WS159_PanzerE_wing_front_mulch_beds',*merge(beds),[MUL])
obj('WS159_PanzerE_wing_bed_edges',*merge([slab(-4.9,0.0,-0.12,0.0,ZW+0.06,0.3),slab(18.3,24.0,-0.12,0.0,ZW+0.06,0.3)]),[EDG])
# --- 4. bank bed b 3.2..8.5 following LiDAR ground (rise to College Ave walk), gap for the steps at a 8.5..10.9 ---
SA0,SA1=8.5,10.9
avals=list(np.arange(-5.0,25.01,0.5)); bvals=list(np.arange(3.2,8.51,0.33))
H=np.zeros((len(avals),len(bvals)))
for i,a in enumerate(avals):
    for j,b in enumerate(bvals):
        z=gz(a,b); H[i,j]=z if z is not None else np.nan
for j in range(len(bvals)):
    col_=H[:,j]; ok=~np.isnan(col_)
    if ok.any(): H[~ok,j]=np.interp(np.flatnonzero(~ok),np.flatnonzero(ok),col_[ok])
from numpy.lib.stride_tricks import sliding_window_view
Hp=np.pad(H,((1,1),(1,1)),mode='edge'); H=sliding_window_view(Hp,(3,3)).mean(axis=(2,3))
H[:,0]=ZW+0.02  # bed meets the walk edge flush (+2 cm)
H=np.maximum.accumulate(np.maximum(H,ZW+0.02),axis=1)  # monotone up-slope toward College Ave
V=[];F=[];idx={}
for i,a in enumerate(avals):
    for j,b in enumerate(bvals):
        idx[i,j]=len(V); V.append(P(a,b,H[i,j]+0.02))
for i in range(len(avals)-1):
    for j in range(len(bvals)-1):
        am=(avals[i]+avals[i+1])/2
        if SA0<am<SA1: continue
        F.append([idx[i,j],idx[i+1,j],idx[i+1,j+1],idx[i,j+1]])
obj('WS159_PanzerE_bank_mulch_bed_LiDAR2023',V,F,[MUL])
# walk-side concrete edge along the bank toe
obj('WS159_PanzerE_bank_toe_edge',*merge([slab(-5.0,SA0,3.2,3.35,ZW+0.08,0.3),slab(SA1,25.0,3.2,3.35,ZW+0.08,0.3)]),[EDG])
# --- 5. steps OSM 312847984 (a 9.7, b 5.5->10) from the walk up the bank: rise from ZW to LiDAR top ---
ztop=float(np.nanmax(H[[k for k,a in enumerate(avals) if SA0<=a<=SA1],-1])); n=max(3,int(round((ztop-ZW)/0.16))); rise=(ztop-ZW)/n
b0=3.2; run=(8.5-b0)/n; st=[]
for k in range(n):
    st.append(slab(SA0,SA1,b0+k*run,8.5,ZW+(k+1)*rise,(k+1)*rise+0.1))
obj('WS159_PanzerE_bank_steps_concrete_OSM312847984',*merge(st),[CON])
print('FIX159 steps',n,round(rise,3),'ztop',round(ztop,2))
# cheek walls either side of the steps
obj('WS159_PanzerE_step_cheek_walls',*merge([slab(SA0-0.2,SA0,3.2,8.5,ztop+0.15,ztop+0.15-ZW+0.1),slab(SA1,SA1+0.2,3.2,8.5,ztop+0.15,ztop+0.15-ZW+0.1)]),[EDG])
# --- 6. wall lanterns (cch_1: black gooseneck arm + lantern under the lettering, at the piers) UNVERIFIED spacing ---
L=[]
for a in (0.9,6.4,11.9,17.4):
    base=P(a,0.0,126.15)
    L.append(slab(a-0.04,a+0.04,0.0,0.45,126.2,0.06))           # arm
    L.append(slab(a-0.11,a+0.11,0.3,0.52,126.15,0.38))          # lantern body
G=[slab(a-0.09,a+0.09,0.32,0.50,126.08,0.26) for a in (0.9,6.4,11.9,17.4)]
obj('WS159_PanzerE_wall_lanterns_black_UNVERIFIED',*merge(L),[BLK])
obj('WS159_PanzerE_wall_lantern_glass',*merge(G),[LGL])
# --- 7. red-brown downspouts at the pavilion front corners (cch_1 left corner) ---
obj('WS159_PanzerE_downspouts_redbrown',*merge([slab(0.15,0.27,0.02,0.14,129.75,129.75-ZW),slab(18.03,18.15,0.02,0.14,129.75,129.75-ZW)]),[DSP])
bpy.ops.wm.save_as_mainfile(filepath=M+'montclair_state_ws159a.blend',compress=False)
print('FIX159 SAVED')
