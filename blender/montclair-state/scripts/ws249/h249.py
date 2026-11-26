# ws249 (standalone, read-only on main): LiDAR ground patch for the SE berm corner of the soccer field's east stand,
# x -186..-168, y 42..72 (first try -174 / 44..70; widened in ws249c to cover the widened delete box) (east of the ws248 patch, same 1 m grid / same bilinear 3x3 LiDAR surface / +2 cm, so the shared
# x = -186 edge meets it exactly). 'ortho' UV by affine fit of the terrain's own 'ortho' UV. Writes h249.json (box only).
import bpy, os, sys, json, numpy as np, warnings; warnings.filterwarnings('ignore')
F='/workspace/nj-scenes/montclair-state/'+os.environ.get('F','montclair_state.blend')
with bpy.data.libraries.load(F) as (a,b): b.objects=['Terrain_LiDAR_DTM_1m']
T=b.objects[0]; me=T.data; M=T.matrix_world; uvl=me.uv_layers['ortho'].data; P=[];U=[]
for p in me.polygons:
    c=M@p.center
    if -230<c.x<-150 and 20<c.y<100:
        for li in p.loop_indices:
            w=M@me.vertices[me.loops[li].vertex_index].co; P.append((w.x,w.y)); U.append(tuple(uvl[li].uv))
P=np.array(P);U=np.array(U);X=np.c_[P,np.ones(len(P))];A=np.linalg.lstsq(X,U,rcond=None)[0]
print('H249 uv fit maxres',round(float(np.abs(X@A-U).max()),6),flush=True)
D='/workspace/nj-scenes/montclair-state/scripts/ws248/'
G23=np.load(D+'g1m_23.npy'); G17=np.load(D+'g1m_17.npy'); G=np.where(np.isfinite(G23),G23,G17); X0,Y0=-320.,-20.
def nb(G,r):
    ny,nx=G.shape; pad=np.pad(G,r,constant_values=np.nan); return np.stack([pad[r+dy:r+dy+ny,r+dx:r+dx+nx] for dy in range(-r,r+1) for dx in range(-r,r+1)])
for r in (1,2,3): G=np.where(np.isfinite(G),G,np.nanmedian(nb(G,r),axis=0))
Gs=np.nanmean(nb(G,1),axis=0)
def gz(x,y):
    fx=x-X0-0.5; fy=y-Y0-0.5; i=int(np.floor(fx)); j=int(np.floor(fy)); tx=fx-i; ty=fy-j
    q=Gs[j:j+2,i:i+2]; return float(q[0,0]*(1-tx)*(1-ty)+q[0,1]*tx*(1-ty)+q[1,0]*(1-tx)*ty+q[1,1]*tx*ty)
xs=np.arange(-186.,-168+0.01,1.0); ys=np.arange(42.,72+0.01,1.0); V=[];idx={}
for j,y in enumerate(ys):
    for i,x in enumerate(xs): idx[(i,j)]=len(V); V.append([float(x),float(y),gz(x,y)+0.02])
Fq=[[idx[(i,j)],idx[(i+1,j)],idx[(i+1,j+1)],idx[(i,j+1)]] for j in range(len(ys)-1) for i in range(len(xs)-1)]
from collections import defaultdict
ec=defaultdict(int)
for f in Fq:
    for k in range(4): ec[tuple(sorted((f[k],f[(k+1)%4])))]+=1
low={}
def lowv(a):
    if a not in low: low[a]=len(V); V.append([V[a][0],V[a][1],V[a][2]-0.6])
    return low[a]
NF=len(Fq)
for f in list(Fq):
    for k in range(4):
        a,b_=f[k],f[(k+1)%4]
        if ec[tuple(sorted((a,b_)))]==1 and not (V[a][0]==-186. and V[b_][0]==-186.): Fq.append([b_,a,lowv(a),lowv(b_)])
UV=[list(map(float,np.array([v[0],v[1],1.0])@A)) for v in V]
print('H249 patch verts',len(V),'top',NF,'skirt',len(Fq)-NF,'z',round(min(v[2] for v in V[:len(idx)]),2),round(max(v[2] for v in V[:len(idx)]),2),flush=True)
json.dump({'V':V,'F':Fq,'UV':UV},open('/workspace/nj-scenes/montclair-state/scripts/ws249/h249.json','w'))
sys.stdout.flush(); os._exit(0)
