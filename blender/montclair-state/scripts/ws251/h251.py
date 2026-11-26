# ws251 (standalone, read-only on main ws250q): W63b Feliciano/Dickson passage — FULL (lower-capable) 1 m LiDAR ground patch
# for the box x -195..-163, y 139..179 (Feliciano E wall x -192, Dickson W wall x ~-182; University Hall starts y 221, untouched).
# z = old + (LiDAR - old) * w, w = 0 at the box edge -> 1 at 3 m in; the old terrain faces inside the box are cut out in f251a.py,
# so this patch is the ground there. 0.3 m skirts; 'ortho' UV by affine fit of the terrain's own UV (same as h250).
import bpy, os, sys, json, numpy as np, warnings; warnings.filterwarnings('ignore')
from mathutils import Vector
from mathutils.bvhtree import BVHTree
F='/workspace/nj-scenes/montclair-state/'+os.environ.get('F','montclair_state.blend')
with bpy.data.libraries.load(F) as (a,b): b.objects=['Terrain_LiDAR_DTM_1m','WS250_W63_lawn_LiDAR2023_ground_patch_1m']
T=b.objects[0]
for o in b.objects: bpy.context.scene.collection.objects.link(o)
me=T.data; M=T.matrix_world; uvl=me.uv_layers['ortho'].data; P=[];U=[]
for p in me.polygons:
    c=M@p.center
    if -230<c.x<-130 and 120<c.y<200:
        for li in p.loop_indices:
            w=M@me.vertices[me.loops[li].vertex_index].co; P.append((w.x,w.y)); U.append(tuple(uvl[li].uv))
P=np.array(P);U=np.array(U);X=np.c_[P,np.ones(len(P))];A=np.linalg.lstsq(X,U,rcond=None)[0]
print('H251 uv fit n',len(P),'maxres',round(float(np.abs(X@A-U).max()),6),flush=True)
dg=bpy.context.evaluated_depsgraph_get(); em=T.evaluated_get(dg).to_mesh()
vs=[M@v.co for v in em.vertices]; ps=[p.vertices[:] for p in em.polygons if any(-260<vs[i].x<-120 and 100<vs[i].y<220 for i in p.vertices)]
bvh=BVHTree.FromPolygons(vs,ps)
def oz(x,y):
    h=bvh.ray_cast(Vector((x,y,400)),Vector((0,0,-1)),600); return h[0].z if h[0] else np.nan
D='/workspace/nj-scenes/montclair-state/scripts/ws248/'
G23=np.load(D+'g1m_23.npy'); G17=np.load(D+'g1m_17.npy'); G=np.where(np.isfinite(G23),G23,G17+0.12); X0,Y0=-320.,-20.
def nb(G,r):
    ny,nx=G.shape; pad=np.pad(G,r,constant_values=np.nan); return np.stack([pad[r+dy:r+dy+ny,r+dx:r+dx+nx] for dy in range(-r,r+1) for dx in range(-r,r+1)])
for r in (1,2,3): G=np.where(np.isfinite(G),G,np.nanmedian(nb(G,r),axis=0))
Gs=np.nanmean(nb(G,1),axis=0)
def gz(x,y):  # cell (i,j) mean sits at the cell CENTRE (i+0.5, j+0.5) (ws249f lesson)
    fx=x-X0-0.5; fy=y-Y0-0.5; i=int(np.floor(fx)); j=int(np.floor(fy)); tx=fx-i; ty=fy-j
    q=Gs[j:j+2,i:i+2]; return float(q[0,0]*(1-tx)*(1-ty)+q[0,1]*tx*(1-ty)+q[1,0]*(1-tx)*ty+q[1,1]*tx*ty)
x0,x1,y0,y1=[float(v) for v in os.environ.get('BOX','-195,-163,139,179').split(',')]; FE=float(os.environ.get('FE','3'))
xs=np.arange(x0,x1+0.01,1.0); ys=np.arange(y0,y1+0.01,1.0); Z={}; R={}; nanl=0
for j,y in enumerate(ys):
    for i,x in enumerate(xs):
        o=oz(x,y); l=gz(x,y); w=float(np.clip(min(x-x0,x1-x,y-y0,y1-y)/FE,0,1))
        if not np.isfinite(l): l=o; nanl+=1
        if not np.isfinite(o): o=l
        z=o+(l-o)*w; Z[(i,j)]=z; R[(i,j)]=z-o
V=[];idx={}
def vid(i,j):
    if (i,j) not in idx: idx[(i,j)]=len(V); V.append([float(xs[i]),float(ys[j]),Z[(i,j)]])
    return idx[(i,j)]
Fq=[[vid(i,j),vid(i+1,j),vid(i+1,j+1),vid(i,j+1)] for j in range(len(ys)-1) for i in range(len(xs)-1)]
from collections import defaultdict
ec=defaultdict(int)
for f in Fq:
    for k in range(4): ec[tuple(sorted((f[k],f[(k+1)%4])))]+=1
low={}
def lowv(a):
    if a not in low: low[a]=len(V); V.append([V[a][0],V[a][1],V[a][2]-0.3])
    return low[a]
NF=len(Fq)
for f in list(Fq[:NF]):
    for k in range(4):
        a,b_=f[k],f[(k+1)%4]
        if ec[tuple(sorted((a,b_)))]==1: Fq.append([b_,a,lowv(a),lowv(b_)])
UV=[list(map(float,np.array([v[0],v[1],1.0])@A)) for v in V]
r=np.array([R[k] for k in R]); print('H251 patch verts',len(V),'top',NF,'skirt',len(Fq)-NF,'change min %.2f max %.2f mean %.2f nanL %d'%(r.min(),r.max(),r.mean(),nanl),flush=True)
json.dump({'V':V,'F':Fq,'UV':UV,'box':[x0,x1,y0,y1]},open('/workspace/nj-scenes/montclair-state/scripts/ws251/h251.json','w'))
sys.stdout.flush(); os._exit(0)
