# ws266 (merge208 CHAIN, on main ws265b): police foundation / outbuilding bare band (ws265 residual).
# f265a/f265b kept new blades >= 0.5 m from any non-ground probe top and faded over 1 m toward it, which left a ~1 m bare
# strip of olive soil around the police foundation and the outbuilding at eye level. Real mown lawns run to a trimmed edge at
# a building foot (string-trimmed, slightly thinner). This pass fills the deficit ONLY inside that band (< 1.6 m from a
# non-ground top): building tops (police roof/parapet/windows/foundation/outbuilding/roof units) may be approached to 0.15 m
# with density easing 40% -> 100% over 0.6 m; walks/deck/deck-base strip keep a 0.3 m clearance with a 0.3 m fade.
# z = inverse-distance mean of the 4 nearest probe265a ground samples - 2 cm (low memory, same as f265b). Mask rebuilt.
# Trimmed-edge look is an assumption (no close photo of the police foundation found) = UNVERIFIED.
import bpy, json, os, numpy as np
from mathutils import Vector
from mathutils.kdtree import KDTree
TAG='F266A'; D='/workspace/nj-scenes/montclair-state/'
G=bpy.data.objects['gd_grass_police_lawn_points']; me=G.data; W=G.matrix_world; Wi=W.inverted()
if me.get('ws266a_band'): raise SystemExit('F266A already applied')
E=np.array([tuple(W@v.co) for v in me.vertices]); n0=len(E)
nt=bpy.data.materials['WS68_Ground_ortho_grass_north2020'].node_tree
x0=nt.nodes['W263_u'].inputs['From Min'].default_value; x1=nt.nodes['W263_u'].inputs['From Max'].default_value
y0=nt.nodes['W263_v'].inputs['From Min'].default_value; y1=nt.nodes['W263_v'].inputs['From Max'].default_value
print(TAG,'box',round(x0,2),round(x1,2),round(y0,2),round(y1,2),'existing',n0,flush=True)
R=json.load(open(D+'scripts/ws265/eval265a.json'))
GOOD=('WS68_RHD_ground_northDTM','M3b_north_LiDAR_DTM_1m_west_rail_corridor')
BLDG=('fp_police_roof','fp_police_parapet','fp_police_windows','fp_police_foundation','fp_police_outbuilding','fp_police_roof_units')
C=np.array([(r[0],r[1]) for r in R])
def lum(c): return 0.2126*c[0]+0.7152*c[1]+0.0722*c[2]
ok=np.array([bool(r[2]) and r[2].startswith(GOOD) and r[4]>0.5 and (r[5] is None or lum(r[5])<0.85) for r in R])
isb=np.array([bool(r[2]) and r[2].startswith(BLDG) for r in R])
iso=np.array([bool(r[2]) and not r[2].startswith(GOOD) and not r[2].startswith(BLDG) for r in R])
def kd(mask):
    t=KDTree(max(1,int(mask.sum())))
    for i,(x,y) in enumerate(C[mask]): t.insert((x,y,0),i)
    t.balance(); return t
kb=kd(isb); ko=kd(iso); kc=kd(np.ones(len(C),bool))
print(TAG,'samples bldg',int(isb.sum()),'other',int(iso.sum()),flush=True)
GR=0.5; NX=int(np.ceil((x1-x0)/GR)); NY=int(np.ceil((y1-y0)/GR))
H=np.zeros((NY,NX)); ii=np.clip(((E[:,0]-x0)/GR).astype(int),0,NX-1); jj=np.clip(((E[:,1]-y0)/GR).astype(int),0,NY-1); np.add.at(H,(jj,ii),1)
def blur(a,s):
    r=int(3*s)+1; k=np.exp(-0.5*(np.arange(-r,r+1)/s)**2); k/=k.sum()
    a=np.apply_along_axis(lambda v:np.convolve(v,k,'same'),0,a); return np.apply_along_axis(lambda v:np.convolve(v,k,'same'),1,a)
# small blur (0.5 m) so the band deficit is not hidden by the dense lawn next to it
B=blur(H,1.0)/(GR*GR); Dc=float(np.percentile(B[H>0],60)); print(TAG,'core density /m2 %.1f'%Dc,flush=True)
rng=np.random.default_rng(2661); new=[]; nb=0
sm=lambda t:(lambda u:u*u*(3-2*u))(min(1.0,max(0.0,t)))
for j in range(NY):
    for i in range(NX):
        cx=x0+(i+.5)*GR; cy=y0+(j+.5)*GR
        db=kb.find((cx,cy,0))[2]; do=ko.find((cx,cy,0))[2]
        if min(db,do)>1.6: continue
        # count actual points in this cell (unblurred) so the band itself is measured
        deficit=Dc-H[j,i]/(GR*GR)
        if deficit<=0.5: continue
        nb+=1
        for _ in range(rng.poisson(deficit*GR*GR)):
            x=cx+rng.uniform(-GR/2,GR/2); y=cy+rng.uniform(-GR/2,GR/2)
            c,ci,dc=kc.find((x,y,0))
            if dc>0.4 or not ok[ci]: continue
            db=kb.find((x,y,0))[2]; do=ko.find((x,y,0))[2]
            if db<0.15 or do<0.3: continue
            de=min(x-x0,x1-x,y-y0,y1-y)
            k=sm((de-0.3)/3.0)*(0.4+0.6*sm((db-0.15)/0.6))*sm((do-0.3)/0.3)
            if rng.random()<k: new.append((x,y))
print(TAG,'band cells',nb,'candidates',len(new),flush=True)
gidx=[k for k,r in enumerate(R) if r[2] and r[2].startswith(GOOD)]; kg=KDTree(len(gidx))
for n,k in enumerate(gidx): kg.insert((R[k][0],R[k][1],0),n)
kg.balance(); P=[]; drop=0
for x,y in new:
    nn=kg.find_n((x,y,0),4)
    if not nn or nn[0][2]>0.4: drop+=1; continue
    w=[1/max(d,0.02) for _,_,d in nn]; z=sum(wi*R[gidx[i]][3] for wi,(_,i,_) in zip(w,nn))/sum(w)
    # guard: never above the nearest ground sample by > 5 cm (no blades climbing a foundation step)
    z=min(z,R[gidx[nn[0][1]]][3]+0.05)
    P.append((x,y,z-0.02))
print(TAG,'snapped',len(P),'dropped',drop,flush=True)
attrs=[a for a in me.attributes if a.domain=='POINT' and a.name!='position' and not a.name.startswith('.')]
print(TAG,'point attrs',[a.name for a in attrs],flush=True)
me.vertices.add(len(P))
co=np.array([tuple(Wi@Vector(p)) for p in P]).ravel()
for k,v in enumerate(me.vertices[n0:]): v.co=co[3*k:3*k+3]
me.update(); me['ws266a_band']=len(P)
print(TAG,'grass points',n0,'->',len(me.vertices),flush=True)
json.dump([list(p) for p in P],open(D+'scripts/ws266/band266a_points.json','w'))
A=np.array([tuple(W@v.co) for v in me.vertices])[:,:2]; Rr=0.25
NX2=int(round((x1-x0)/Rr)); NY2=int(round((y1-y0)/Rr))
H2=np.zeros((NY2,NX2)); ii=np.clip(((A[:,0]-x0)/Rr).astype(int),0,NX2-1); jj=np.clip(((A[:,1]-y0)/Rr).astype(int),0,NY2-1); np.add.at(H2,(jj,ii),1)
B2=blur(H2,0.6/Rr); core=np.percentile(B2[H2>0],60); M=np.clip(B2/core,0,1); M=M*M*(3-2*M)
os.makedirs(D+'data/ws266',exist_ok=True); fn=D+'data/ws266/police_grass_density266a.png'
tmp=bpy.data.images.new('W266_tmp',NX2,NY2,alpha=False); px=np.ones((NY2,NX2,4),np.float32); px[...,0]=px[...,1]=px[...,2]=M
tmp.pixels.foreach_set(px.ravel()); tmp.filepath_raw=fn; tmp.file_format='PNG'; tmp.save(); bpy.data.images.remove(tmp)
old=nt.nodes['W263_mask'].image
img=bpy.data.images.load(fn); img.name='W266_police_grass_density266a'; img.filepath='//data/ws266/police_grass_density266a.png'; img.colorspace_settings.name='Non-Color'
print(TAG,'mask',img.size[:],'mean %.3f'%M.mean(),flush=True)
for mn in ('WS68_Ground_ortho_grass_north2020','North_ground_ortho2020.001'):
    bpy.data.materials[mn].node_tree.nodes['W263_mask'].image=img; print(TAG,'mask ->',mn,flush=True)
if old and old.users==0: bpy.data.images.remove(old)
