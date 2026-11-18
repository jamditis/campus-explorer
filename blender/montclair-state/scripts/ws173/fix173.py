# ws173: UNIFY #78 part 1 — residential driveways S of Normal Ave W (ground surface only; houses stay out per BOUNDARY.md)
# Evidence: 2023 NJ LiDAR J5D5 class-2 intensity (prep/ws172_s77/las172.npy) in the road frame (A=(-268.8,-262.9) on the N edge,
# s north-positive, t east-positive): three dark (<3k) N-S strips running from the gutter (s -9.75) to the house fronts (class-6 at s -21):
# D1 t -75.5..-71.0 (flares W to -77.0 by the house), D2 t -57.0..-52.75, D3 t -42.0..-37.5 widening to -42.5..-35.0 behind s -15.5.
# NJOGIS 2020 ortho (prep/ws173_drives/ortho173_grid.png) shows parked cars on D2 and D3. A 4th dark patch (t -24..-18, s -13..-20) has no
# dark link to the curb and the ortho shows a concrete walk there -> not built (UNVERIFIED).
# Design: curb depressed to 3 cm over each mouth with 1.0 m wings; S walk front lowered to match (ramped across the walk);
# asphalt drive surface from the curb back to the house front, laid 6 mm over the (lowered) walk because the LiDAR is dark across the
# walk band at all three (asphalt crossing; UNVERIFIED), lawn edges 1–3 cm above the drive, 8 cm side skirts.
import bpy, bmesh, math, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
OB=bpy.data.objects
for o in [o for o in OB if o.name.startswith('WS173_')]: OB.remove(o)
A=np.array([-268.8,-262.9]); N=np.array([0.236,1.0]); N/=np.linalg.norm(N); T=np.array([N[1],-N[0]])
def st(x,y): d=np.array((x,y))-A; return float(d@N), float(d@T)
def xy(s,t): p=A+N*s+T*t; return float(p[0]),float(p[1])
D=np.load('/workspace/nj-scenes/montclair-state/prep/ws172_s77/dtm172.npy')[0]; X0,Y0,R=-360.0,-315.0,0.5
def dz(x,y):
    fi=(x-X0)/R-0.5; fj=(y-Y0)/R-0.5
    i=int(min(max(math.floor(fi),0),D.shape[1]-2)); j=int(min(max(math.floor(fj),0),D.shape[0]-2)); tx=min(max(fi-i,0),1); ty=min(max(fj-j,0),1)
    return float(D[j,i]*(1-tx)*(1-ty)+D[j,i+1]*tx*(1-ty)+D[j+1,i]*(1-tx)*ty+D[j+1,i+1]*tx*ty)
DR=[('D1',-75.5,-71.0,-77.0,-70.75,-17.5,-20.8),('D2',-57.0,-52.75,-57.0,-52.75,-17.5,-20.8),('D3',-42.0,-37.5,-42.5,-35.0,-15.5,-21.5)]
WING=1.0
def wdep(t):   # 1 inside a mouth, ramps to 0 over WING
    w=0.0
    for _,a,b,*__ in DR:
        if a<=t<=b: return 1.0
        f=min(abs(t-a),abs(t-b))
        if f<WING: w=max(w,1-f/WING)
    return w
# --- 1. depress the S curb (top verts) ---
cu=OB['WS163_NormalAve_W_S_curb_UNVERIFIEDsection']; mw=cu.matrix_world; mi=mw.inverted(); me=cu.data
grp={}
for v in me.vertices:
    w=mw@v.co; grp.setdefault((round(w.x,3),round(w.y,3)),[]).append(v)
nc=0
for k,vs in grp.items():
    if len(vs)<2: continue
    s,t=st(*k); f=wdep(t)
    if f<=0: continue
    vs=sorted(vs,key=lambda v:(mw@v.co).z); top=vs[-1]; bot=vs[0]
    wt=mw@top.co; ze=wt.z-0.15          # top was road edge + 0.15
    wt.z=ze+0.15-0.12*f; top.co=mi@wt; nc+=1
me.update(); print('FIX173 curb top verts lowered',nc,flush=True)
# --- 2. ramp the S walk across each mouth: front row lowered 0.12*f, back row unchanged ---
sw=OB['WS163_NormalAve_W_S_sidewalk_1p6m_UNVERIFIED']; mw2=sw.matrix_world; mi2=mw2.inverted()
ss=[st((mw2@v.co).x,(mw2@v.co).y)[0] for v in sw.data.vertices]; sfront=max(ss); sback=min(ss); W=sfront-sback
nw=0
for v in sw.data.vertices:
    w=mw2@v.co; s,t=st(w.x,w.y); f=wdep(t)
    if f<=0: continue
    u=(s-sback)/W   # 1 at the front (curb), 0 at the back
    w.z-=0.12*f*u; v.co=mi2@w; nw+=1
sw.data.update(); print('FIX173 walk verts ramped',nw,'sfront',round(sfront,2),'sback',round(sback,2),flush=True)
# --- 3. BVH of the surfaces the drive must sit on/over ---
dg=bpy.context.evaluated_depsgraph_get()
def bvh(names):
    out=[]
    for n in names:
        o=OB.get(n)
        if not o: continue
        oe=o.evaluated_get(dg); m=oe.to_mesh(); m.transform(o.matrix_world)
        out.append(BVHTree.FromPolygons([v.co.copy() for v in m.vertices],[tuple(p.vertices) for p in m.polygons])); oe.to_mesh_clear()
    return out
WALK=bvh(['WS163_NormalAve_W_S_sidewalk_1p6m_UNVERIFIED']); CURB=bvh(['WS163_NormalAve_W_S_curb_UNVERIFIEDsection'])
LAWN=bvh(['WS172_frontyards_S_of_NormalAve_W_DTM2023_J5D5','WS163_walk_back_lawn_lip_S_UNVERIFIED','WS110_ground_patch_S_of_y-238_DTM2023_1m_lawn_UNVERIFIED','WS163_ground_patch_W_of_WS110_LiDAR2023_1m_UNVERIFIED'])
def top(trees,x,y):
    z=None
    for b in trees:
        h=b.ray_cast(Vector((x,y,200)),Vector((0,0,-1)),300)
        if h[0] is not None and (z is None or h[0].z>z): z=h[0].z
    return z
# --- 4. drive surfaces ---
def getmat():
    m=bpy.data.materials.get('WS173_driveway_asphalt_aged_UNVERIFIED')
    if m: return m
    m=bpy.data.materials.new('WS173_driveway_asphalt_aged_UNVERIFIED'); m.use_nodes=True; nt=m.node_tree; b=nt.nodes['Principled BSDF']
    tc=nt.nodes.new('ShaderNodeTexCoord'); nz=nt.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value=1.6; nz.inputs['Detail'].default_value=8
    cr=nt.nodes.new('ShaderNodeValToRGB'); cr.color_ramp.elements[0].color=(0.085,0.083,0.08,1); cr.color_ramp.elements[1].color=(0.19,0.185,0.175,1)
    nt.links.new(tc.outputs['Object'],nz.inputs['Vector']); nt.links.new(nz.outputs['Fac'],cr.inputs['Fac']); nt.links.new(cr.outputs['Color'],b.inputs['Base Color'])
    b.inputs['Roughness'].default_value=0.9; return m
mat=getmat()
col=bpy.data.collections.get('WS173_driveways') or bpy.data.collections.new('WS173_driveways')
if col.name not in bpy.context.scene.collection.children: bpy.context.scene.collection.children.link(col)
S0=-11.30   # model curb face (road edge)
for nm,a,b,a2,b2,sfl,send in DR:
    svals=[S0,sfront,(sfront+sback)/2,sback]+list(np.arange(sback-0.45,send-0.001,-0.5))+[send]
    def tr(s):   # t-range at s (linear flare between sfl+1 and sfl)
        if s>=sfl+1.0: return a,b
        if s<=sfl: return a2,b2
        u=(sfl+1.0-s)/1.0; return a+(a2-a)*u, b+(b2-b)*u
    NT=int(max(b-a,b2-a2)/0.25)+1
    Z=np.zeros((len(svals),NT)); P=[]; LZ={}
    for i,s in enumerate(svals):
        ta,tb=tr(s); row=[]
        for j in range(NT):
            t=ta+(tb-ta)*j/(NT-1); x,y=xy(s,t); row.append((x,y))
            if s>=sback-0.01:
                if s>sfront+0.01:   # curb top (depressed): sample just behind the curb face
                    xc,yc=xy(-11.39,t); zw=top(CURB,xc,yc)
                else:
                    xc,yc=xy(max(min(s,sfront-0.03),sback+0.03),t); zw=top(WALK,xc,yc)
                zl=top(LAWN,x,y)
                zz=zw if zw is not None else dz(x,y)
                if zl is not None and s<sback+0.3: zz=max(zz,zl)
                Z[i,j]=zz+0.006
            else:
                zl=top(LAWN,x,y); z0=dz(x,y)+0.02
                Z[i,j]=max(z0,(zl+0.012) if zl is not None else z0); LZ[(i,j)]=zl
        P.append(row)
    # smooth along s behind the walk (3-tap), keep the walk band exact
    k=[i for i,s in enumerate(svals) if s<sback-0.01]
    Zs=Z.copy()
    for i in k[1:-1]: Zs[i]=(Z[i-1]+Z[i]+Z[i+1])/3
    for (i,j),zl in LZ.items():
        if zl is not None: Zs[i,j]=max(Zs[i,j],zl+0.008)
    Z=Zs
    bm=bmesh.new(); V=[[bm.verts.new((P[i][j][0],P[i][j][1],Z[i,j])) for j in range(NT)] for i in range(len(svals))]
    for i in range(len(svals)-1):
        for j in range(NT-1): bm.faces.new((V[i][j],V[i][j+1],V[i+1][j+1],V[i+1][j]))
    # side skirts (8 cm) on both long edges + far end
    for side in (0,NT-1):
        Sk=[bm.verts.new((v.co.x,v.co.y,v.co.z-0.08)) for v in [V[i][side] for i in range(len(svals))]]
        for i in range(len(svals)-1): bm.faces.new((V[i][side],V[i+1][side],Sk[i+1],Sk[i]))
    Sk=[bm.verts.new((v.co.x,v.co.y,v.co.z-0.08)) for v in V[-1]]
    for j in range(NT-1): bm.faces.new((V[-1][j],V[-1][j+1],Sk[j+1],Sk[j]))
    bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
    me=bpy.data.meshes.new(nm); bm.to_mesh(me); bm.free(); me.materials.append(mat)
    for p in me.polygons: p.use_smooth=False
    o=OB.new(f'WS173_driveway_{nm}_S_of_NormalAve_W_LiDAR2023_int_UNVERIFIED',me); col.objects.link(o)
    # report how far lawn sits above the drive centreline behind the walk
    print('FIX173',nm,'rows',len(svals),'cols',NT,'z',round(float(Z.min()),2),round(float(Z.max()),2),flush=True)
print('FIX173 done',flush=True)
