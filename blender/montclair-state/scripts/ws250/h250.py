# ws250 (standalone, read-only on main ws249f): W63 raise-only LiDAR ground patch for the lawn N of Dickson Hall / E of Feliciano
# (x -192..-110 (ws250 east extension to Calcia's W side), y 161..212; University Hall's footprint starts at y 221). The terrain there is big PB fan faces 0.6-1.3 m BELOW
# the 2023/2017 LiDAR (agree ~0.12 m); vertex snapping/subdividing them gave creases (ws250a-g, discarded). The patch is a 1 m grid:
# z = max(old, old + (LiDAR - old) * w) + 0.02 (w = 0 at the edge -> 1 at 4 m in), so it only ever RAISES the ground and meets
# the old terrain at its edge; quads with no vertex raised > 5 cm are dropped. 0.3 m skirts on the outline. 'ortho' UV by affine
# fit of the terrain's own UV. Joined INTO Terrain_LiDAR_DTM_1m by GN (f250p.py) so Footpaths_OSM's drape lands on it.
import bpy, os, sys, json, numpy as np, warnings; warnings.filterwarnings('ignore')
from mathutils import Vector
from mathutils.bvhtree import BVHTree
F='/workspace/nj-scenes/montclair-state/'+os.environ.get('F','montclair_state.blend')
with bpy.data.libraries.load(F) as (a,b): b.objects=['Terrain_LiDAR_DTM_1m']
T=b.objects[0]; bpy.context.scene.collection.objects.link(T); me=T.data; M=T.matrix_world; uvl=me.uv_layers['ortho'].data; P=[];U=[]
for p in me.polygons:
    c=M@p.center
    if -200<c.x<-104 and 150<c.y<220:
        for li in p.loop_indices:
            w=M@me.vertices[me.loops[li].vertex_index].co; P.append((w.x,w.y)); U.append(tuple(uvl[li].uv))
P=np.array(P);U=np.array(U);X=np.c_[P,np.ones(len(P))];A=np.linalg.lstsq(X,U,rcond=None)[0]
print('H250 uv fit n',len(P),'maxres',round(float(np.abs(X@A-U).max()),6),flush=True)
dg=bpy.context.evaluated_depsgraph_get(); em=T.evaluated_get(dg).to_mesh()
vs=[M@v.co for v in em.vertices]; ps=[p.vertices[:] for p in em.polygons if any(-200<vs[i].x<-104 and 150<vs[i].y<220 for i in p.vertices)]
bvh=BVHTree.FromPolygons(vs,ps)
def oz(x,y):
    h=bvh.ray_cast(Vector((x,y,400)),Vector((0,0,-1)),600); return h[0].z if h[0] else np.nan
D='/workspace/nj-scenes/montclair-state/scripts/ws248/'
G23=np.load(D+'g1m_23.npy'); G17=np.load(D+'g1m_17.npy'); G0=np.where(np.isfinite(G23),G23,G17+0.12); X0,Y0=-320.,-20.
# ws250: east extension (x -160..-100, y 140..230, 2023 J5D6) -> one grid x -320..-100, y -20..230
E=np.load('/workspace/nj-scenes/montclair-state/scripts/ws250/g1m_e23.npy'); G=np.full((250,220),np.nan); G[0:240,0:180]=G0
Gs_=G[160:250,160:220]; G[160:250,160:220]=np.where(np.isfinite(Gs_),Gs_,E)
def nb(G,r):
    ny,nx=G.shape; pad=np.pad(G,r,constant_values=np.nan); return np.stack([pad[r+dy:r+dy+ny,r+dx:r+dx+nx] for dy in range(-r,r+1) for dx in range(-r,r+1)])
for r in (1,2,3): G=np.where(np.isfinite(G),G,np.nanmedian(nb(G,r),axis=0))
Gs=np.nanmean(nb(G,1),axis=0)
def gz(x,y):
    fx=x-X0-0.5; fy=y-Y0-0.5; i=int(np.floor(fx)); j=int(np.floor(fy)); tx=fx-i; ty=fy-j
    q=Gs[j:j+2,i:i+2]; return float(q[0,0]*(1-tx)*(1-ty)+q[0,1]*tx*(1-ty)+q[1,0]*(1-tx)*ty+q[1,1]*tx*ty)
x0,x1,y0,y1=-192.,-110.,161.,212.
xs=np.arange(x0,x1+0.01,1.0); ys=np.arange(y0,y1+0.01,1.0); Z={}; R={}
for j,y in enumerate(ys):
    for i,x in enumerate(xs):
        o=oz(x,y); l=gz(x,y); w=float(np.clip(min(x-x0,x1-x,y-y0,y1-y)/4.0,0,1))
        if not np.isfinite(o): o=l
        z=max(o,o+(l-o)*w); Z[(i,j)]=z+0.02; R[(i,j)]=z-o
keep=[(i,j) for j in range(len(ys)-1) for i in range(len(xs)-1) if max(R[(i,j)],R[(i+1,j)],R[(i+1,j+1)],R[(i,j+1)])>0.05]
V=[];idx={}
def vid(i,j):
    if (i,j) not in idx: idx[(i,j)]=len(V); V.append([float(xs[i]),float(ys[j]),Z[(i,j)]])
    return idx[(i,j)]
Fq=[[vid(i,j),vid(i+1,j),vid(i+1,j+1),vid(i,j+1)] for (i,j) in keep]
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
r=np.array([R[k] for k in R]); print('H250 patch verts',len(V),'top',NF,'skirt',len(Fq)-NF,'raise max %.2f mean(raised>5cm) %.2f'%(r.max(),r[r>0.05].mean()),flush=True)
json.dump({'V':V,'F':Fq,'UV':UV},open('/workspace/nj-scenes/montclair-state/scripts/ws250/h250.json','w'))
sys.stdout.flush(); os._exit(0)
