# ws175b: WS110 S walk back edge — the 1 m ground grid met the walk in a sawtooth (pre-existing, visible in the ws174c before-shot)
# and left dark slivers after the #80 shift. Same treatment as WS163_walk_back_lawn_lip_S: a 1.4 m lawn lip strip from the walk back edge
# (z = walk top) blending onto the evaluated ground (+3 cm) + ground verts under the lip sunk 3 cm below it. t 1.3..196.
import bpy, bmesh, math, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
OB=bpy.data.objects
A=np.array([-268.8,-262.9]); N=np.array([0.236,1.0]); N/=np.linalg.norm(N); T=np.array([N[1],-N[0]])
def face(t): return -0.01446*t-11.028
def D110(t):
    if t<0.9 or t>196: return 0.0
    if t<=176: return 0.75
    u=(t-176)/20.0; return 0.75*0.5*(1+math.cos(math.pi*u))
for o in [o for o in OB if o.name.startswith('WS175_WS110_walk_back_lawn_lip_S')]: OB.remove(o)
wk=next(o for o in OB if o.name.startswith('WS110_NormalAve_sidewalk_ws85'))
gr=next(o for o in OB if o.name.startswith('WS110_ground_patch_S_of_y-238'))
mw=wk.matrix_world; rows={}
for v in wk.data.vertices:
    w=mw@v.co; d=np.array((w.x,w.y))-A; s=float(d@N); t=float(d@T); off=s-face(t)-D110(t)
    if 1.0<t<196 and -1.9<off<-1.7:
        k=round(t,1); 
        if k not in rows or w.z>rows[k][2]: rows[k]=(w.x,w.y,w.z,t)
R=[rows[k] for k in sorted(rows)]
# prepend the bridge walk's W-end back corner (t ~ -0.82) so the lip also covers the 2 m junction bridge (dark slit at the pole)
bw=[o for o in OB if o.name.startswith('WS174_junction_bridge_S_walk')]
if bw:
    c=[]
    for v in bw[0].data.vertices:
        w=bw[0].matrix_world@v.co; d=np.array((w.x,w.y))-A; c.append((float(d@N),float(d@T),w.x,w.y,w.z))
    W0=[q for q in c if q[1]<0]; 
    if W0:
        q=min(W0,key=lambda q:(q[0],-q[4])); R.insert(0,(q[2],q[3],q[4],q[1])); print('LIP175 bridge start t %.2f s %.2f'%(q[1],q[0]),flush=True)
# merge near-duplicate stations
R2=[]
for r in R:
    if R2 and abs(r[3]-R2[-1][3])<0.3: continue
    R2.append(r)
# densify to <=1 m
P=[]
for a,b in zip(R2[:-1],R2[1:]):
    n=max(1,int(math.ceil(abs(b[3]-a[3])/1.0)))
    for i in range(n): u=i/n; P.append(tuple(a[j]+(b[j]-a[j])*u for j in range(4)))
P.append(R2[-1]); print('LIP175 stations',len(P),'t %.1f..%.1f'%(P[0][3],P[-1][3]),flush=True)
dg=bpy.context.evaluated_depsgraph_get(); ge=gr.evaluated_get(dg); me=ge.to_mesh(); me.transform(gr.matrix_world)
bvh=BVHTree.FromPolygons([v.co.copy() for v in me.vertices],[tuple(p.vertices) for p in me.polygons]); ge.to_mesh_clear()
def gz(x,y,z0):
    h=bvh.ray_cast(Vector((x,y,z0+20)),Vector((0,0,-1)),60)
    return h[0].z if h[0] else None
OFFS=[0.0,0.35,0.7,1.05,1.4]; W=[0.0,0.5,0.85,1.0,1.0]; ADD=[0,0.03,0.03,0.02,-0.04]
bm=bmesh.new(); grid=[]
for (x,y,z,t) in P:
    row=[]
    for o_,w_ in zip(OFFS,W):
        px=x-N[0]*o_; py=y-N[1]*o_
        g=gz(px,py,z); zz=z-0.005 if o_==0 else ((1-w_)*(z-0.005)+w_*((g if g is not None else z)+ADD[OFFS.index(o_)]))
        row.append(bm.verts.new((px,py,zz)))
    grid.append(row)
for i in range(len(grid)-1):
    for j in range(len(OFFS)-1):
        bm.faces.new((grid[i][j],grid[i+1][j],grid[i+1][j+1],grid[i][j+1]))
bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
for f in bm.faces:
    if f.normal.z<0: f.normal_flip()
lm=bpy.data.meshes.new('WS175_lip'); bm.to_mesh(lm); bm.free()
src=next(o for o in OB if o.name.startswith('WS163_walk_back_lawn_lip_S'))
lm.materials.append(src.data.materials[0])
for p in lm.polygons: p.use_smooth=True
lip=OB.new('WS175_WS110_walk_back_lawn_lip_S_UNIFY80_UNVERIFIED',lm); (gr.users_collection[0] if gr.users_collection else bpy.context.scene.collection).objects.link(lip)
# sink ground verts under the lip / walk back zone below the lip surface
lb=BVHTree.FromPolygons([v.co.copy() for v in lm.vertices],[tuple(p.vertices) for p in lm.polygons])
gmw=gr.matrix_world; gmi=gmw.inverted(); k=0
for v in gr.data.vertices:
    w=gmw@v.co; d=np.array((w.x,w.y))-A; s=float(d@N); t=float(d@T)
    if not (1.0<t<196): continue
    off=s-face(t)-D110(t)
    if not (-2.75<off<-1.75): continue
    h=lb.ray_cast(Vector((w.x,w.y,w.z+20)),Vector((0,0,-1)),60)
    if h[0] and w.z>h[0].z-0.03:
        w.z=h[0].z-0.03; v.co=gmi@w; k+=1
gr.data.update(); print('LIP175 lip faces',len(lm.polygons),'ground sunk',k,flush=True)
