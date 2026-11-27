# ws265b (merge208 CHAIN, after f265a): the ws265a WIPs (eye from S, close-up) showed bald grey patches inside the fill = samples
# rejected by the luminance test (ortho 0.55–0.85 = sun-bleached lawn spots, ~10% of the W-centre). Second pass = f265a with the
# luminance cut at 0.85 (z from the probe samples, no modifier evaluation) (still drops the white band along the deck face, lum > 0.9), deficit measured against ALL current points.
# ws265 (merge208 CHAIN): police flat lawn. probe265a (eval265a.json, 0.35 m jittered grid on main's EVALUATED ground) shows the
# merged north grass is an L (N band + strip along Red Hawk Deck); the rest of the same lawn (WS68 ground W-centre, and the
# M3b west-rail-corridor DTM W of it) reads as flat grey-green ortho with no blades. Same ortho tone as under the existing grass
# (2020 NJ ortho: mown lawn). Fill the deficit to the existing core density: valid = top is WS68/M3b ground, normal z > 0.5,
# ortho luminance < 0.55 (drops the pale band along the deck face), >= 0.5 m from any non-ground top. Fade over 3 m toward the
# W263 mask-box edge and over 1 m toward non-ground. New points are ray-snapped to the evaluated top - 1 cm and get the point
# attributes of a random existing point. Then rebuild the W263 soil mask (same box/grid) from all points -> //data/ws265/.
import bpy, json, os, numpy as np, bmesh
from mathutils import Vector
from mathutils.kdtree import KDTree
TAG='F265B'; D='/workspace/nj-scenes/montclair-state/'
G=bpy.data.objects['gd_grass_police_lawn_points']; me=G.data; W=G.matrix_world; Wi=W.inverted()
if me.get('ws265b_fill'): raise SystemExit('F265B already applied')
E=np.array([tuple(W@v.co) for v in me.vertices]); n0=len(E)
nt=bpy.data.materials['WS68_Ground_ortho_grass_north2020'].node_tree
x0=nt.nodes['W263_u'].inputs['From Min'].default_value; x1=nt.nodes['W263_u'].inputs['From Max'].default_value
y0=nt.nodes['W263_v'].inputs['From Min'].default_value; y1=nt.nodes['W263_v'].inputs['From Max'].default_value
print(TAG,'box',round(x0,2),round(x1,2),round(y0,2),round(y1,2),'existing',n0,flush=True)
R=json.load(open(D+'scripts/ws265/eval265a.json'))
GOOD=('WS68_RHD_ground_northDTM','M3b_north_LiDAR_DTM_1m_west_rail_corridor')
C=np.array([(r[0],r[1]) for r in R])
def lum(c): return 0.2126*c[0]+0.7152*c[1]+0.0722*c[2]
ok=np.array([bool(r[2]) and r[2].startswith(GOOD) and r[4]>0.5 and (r[5] is None or lum(r[5])<0.85) for r in R])
bad=np.array([bool(r[2]) and not r[2].startswith(GOOD) for r in R])
kb=KDTree(int(bad.sum()))
for i,(x,y) in enumerate(C[bad]): kb.insert((x,y,0),i)
kb.balance(); kc=KDTree(len(C))
for i,(x,y) in enumerate(C): kc.insert((x,y,0),i)
kc.balance()
# existing density on a 0.5 m grid, blurred sigma 0.5 m
GR=0.5; NX=int(np.ceil((x1-x0)/GR)); NY=int(np.ceil((y1-y0)/GR))
H=np.zeros((NY,NX)); ii=np.clip(((E[:,0]-x0)/GR).astype(int),0,NX-1); jj=np.clip(((E[:,1]-y0)/GR).astype(int),0,NY-1); np.add.at(H,(jj,ii),1)
def blur(a,s):
    r=int(3*s)+1; k=np.exp(-0.5*(np.arange(-r,r+1)/s)**2); k/=k.sum()
    a=np.apply_along_axis(lambda v:np.convolve(v,k,'same'),0,a); return np.apply_along_axis(lambda v:np.convolve(v,k,'same'),1,a)
B=blur(H,1.0)/(GR*GR); Dc=float(np.percentile(B[H>0],60)); print(TAG,'core density /m2 %.1f'%Dc,flush=True)
rng=np.random.default_rng(2652); new=[]
for j in range(NY):
    for i in range(NX):
        cx=x0+(i+.5)*GR; cy=y0+(j+.5)*GR
        deficit=Dc-B[j,i]
        if deficit<=0.5: continue
        for _ in range(rng.poisson(deficit*GR*GR)):
            x=cx+rng.uniform(-GR/2,GR/2); y=cy+rng.uniform(-GR/2,GR/2)
            c,ci,dc=kc.find((x,y,0))
            if dc>0.4 or not ok[ci]: continue
            db=kb.find((x,y,0))[2] if bad.any() else 99
            if db<0.5: continue
            de=min(x-x0,x1-x,y-y0,y1-y)
            t=min(1,max(0,(de-0.3)/3.0)); t2=min(1,max(0,(db-0.5)/1.0)); k=t*t*(3-2*t)*(t2*t2*(3-2*t2))
            if rng.random()<k: new.append((x,y))
print(TAG,'candidates',len(new),flush=True)
# low-memory snap (ws265b retry; the evaluated snap was killed by the watchdog with the host balloon at ~3.3 GB available):
# z = inverse-distance mean of the 4 nearest probe265a ground samples (0.35 m grid on the EVALUATED ground) - 2 cm; a point is
# dropped if its nearest sample is > 0.4 m away or any of the 4 is not WS68/M3b ground.
gidx=[k for k,r in enumerate(R) if r[2] and r[2].startswith(GOOD)]; kg=KDTree(len(gidx))
for n,k in enumerate(gidx): kg.insert((R[k][0],R[k][1],0),n)
kg.balance(); P=[]; drop=0; on=[]
for x,y in new:
    nn=kg.find_n((x,y,0),4)
    if not nn or nn[0][2]>0.4 or any(kb.find((x,y,0))[2]<0.5 for _ in [0]): drop+=1; continue
    w=[1/max(d,0.02) for _,_,d in nn]; z=sum(wi*R[gidx[i]][3] for wi,(_,i,_) in zip(w,nn))/sum(w)
    P.append((x,y,z-0.02))
print(TAG,'snapped (IDW of probe samples)',len(P),'dropped',drop,flush=True)
# append verts + copy point attributes from random existing points
attrs=[a for a in me.attributes if a.domain=='POINT' and a.name!='position' and not a.name.startswith('.')]
vals={}
for a in attrs:
    n=len(a.data); key='value' if hasattr(a.data[0],'value') else ('vector' if hasattr(a.data[0],'vector') else 'color')
    arr=[getattr(d,key) for d in a.data]; vals[a.name]=(key,arr)
print(TAG,'point attrs',[(a.name,a.data_type) for a in attrs],flush=True)
src=rng.integers(0,n0,len(P))
me.vertices.add(len(P))
co=np.array([tuple(Wi@Vector(p)) for p in P]).ravel()
for k,v in enumerate(me.vertices[n0:]): v.co=co[3*k:3*k+3]
for a in me.attributes:
    if a.name in vals:
        key,arr=vals[a.name]
        for k in range(len(P)):
            v=arr[src[k]]; setattr(a.data[n0+k],key,v)
me.update(); me['ws265b_fill']=len(P)
print(TAG,'grass points',n0,'->',len(me.vertices),flush=True)
# rebuild the W263 soil mask from all points, same box/grid as f263e (0.25 m, sigma 0.6 m, smoothstep of density / p60)
A=np.array([tuple(W@v.co) for v in me.vertices])[:,:2]; Rr=0.25
NX2=int(round((x1-x0)/Rr)); NY2=int(round((y1-y0)/Rr))
H2=np.zeros((NY2,NX2)); ii=np.clip(((A[:,0]-x0)/Rr).astype(int),0,NX2-1); jj=np.clip(((A[:,1]-y0)/Rr).astype(int),0,NY2-1); np.add.at(H2,(jj,ii),1)
B2=blur(H2,0.6/Rr); core=np.percentile(B2[H2>0],60); M=np.clip(B2/core,0,1); M=M*M*(3-2*M)
os.makedirs(D+'data/ws265',exist_ok=True); fn=D+'data/ws265/police_grass_density265b.png'
tmp=bpy.data.images.new('W265_tmp',NX2,NY2,alpha=False); px=np.ones((NY2,NX2,4),np.float32); px[...,0]=px[...,1]=px[...,2]=M
tmp.pixels.foreach_set(px.ravel()); tmp.filepath_raw=fn; tmp.file_format='PNG'; tmp.save(); bpy.data.images.remove(tmp)
old=nt.nodes['W263_mask'].image
img=bpy.data.images.load(fn); img.name='W265_police_grass_density265b'; img.filepath='//data/ws265/police_grass_density265b.png'; img.colorspace_settings.name='Non-Color'
print(TAG,'mask',img.size[:],'old',old.size[:] if old else None,'mean %.3f'%M.mean(),flush=True)
for mn in ('WS68_Ground_ortho_grass_north2020','North_ground_ortho2020.001'):
    bpy.data.materials[mn].node_tree.nodes['W263_mask'].image=img; print(TAG,'mask ->',mn,flush=True)
if old and old.users==0: bpy.data.images.remove(old)
