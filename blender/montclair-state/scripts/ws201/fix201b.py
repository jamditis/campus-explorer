# ws201 W19 (rev b): the thin wavy dark line in the Sprague-lot S bay (WS75/WS80 seam).
# Diagnosis (probe p201a, 0.1 m top-object grid with real GN terrain, projected onto the ws200a close-up): every pixel of the dark line sits
# on a WS75 | WS80 (| WS81 underlay) boundary. Cross-sections: WS75 stands ~1-1.5 cm ABOVE WS80 at its edge (beyond the 4 cm/m lot fall) and
# the WS81 underlay shows in 1-2 cell gaps 2-5 mm low -> a 1 cm riser facing the low sun = dark wavy "crack" with nicks. fix200c failed because it
# only lifted the hidden overlap verts; the visible low side stayed low.
# Designer call: one continuous asphalt mat with flush joints (2020 ortho shows no joint/patch line in this bay; real paving passes are
# rolled flush). RAISE-ONLY: H = current top of the lot sheets on a 0.1 m grid; envelope T = iterate max(H, gauss(T, 0.5 m)) (fills the low side
# of every step with a smooth ramp, keeps the high side, leaves the plain grade alone); applied within 1.6 m of the seams (smooth feather),
# lift capped 4 cm. Every lot sheet vertex goes to >= T + bias (WS75 +2 mm, WS80/WS94/WS96 +1 mm, WS81 underlay -2 mm), so all sheets meet on one
# surface; paint on the lot gets the same delta (stays flush on top). Nothing is lowered (terrain GN re-snaps under paving).
import bpy, numpy as np, math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
X0,X1,Y0,Y1=-263.0,-213.0,-108.5,-93.0; ST=0.1; SIG=0.5; CORR=1.6; CAP=0.04
PFX={'WS75_sprague_lot_asphalt':0.002,'WS80_sprague_lot_fill_asphalt':0.001,'WS94_lot_slit_filler':0.001,'WS96_lot_E_edge_gap_filler':0.001,'WS81_lot_seam_underlay':float(__import__('os').environ.get('B81','-0.002'))}
SH=[];BI={}
for o in bpy.data.objects:
    if o.type!='MESH': continue
    for p,b in PFX.items():
        if o.name.startswith(p): SH.append(o); BI[o.name]=b
LANE=[o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith('WS82_sprague_lane_onesurface')]
V=[];F=[];OID=[]
for k,o in enumerate(SH+LANE):
    mw=o.matrix_world; b=len(V); V+=[mw@v.co for v in o.data.vertices]
    for p in o.data.polygons: F.append(tuple(b+i for i in p.vertices)); OID.append(k)
T=BVHTree.FromPolygons(V,F)
xs=np.arange(X0,X1+1e-6,ST); ys=np.arange(Y0,Y1+1e-6,ST)
H=np.full((len(xs),len(ys)),np.nan); K=np.full(H.shape,-1)
for i,x in enumerate(xs):
    for j,y in enumerate(ys):
        h=T.ray_cast(Vector((x,y,300)),Vector((0,0,-1)))
        if h[0] is not None: H[i,j]=h[0].z; K[i,j]=OID[h[2]]
nS=len(SH)
# seam cells: top object changes between lot sheets (not the lane)
A=(K>=0)&(K<nS)
S=np.zeros(H.shape,bool)
c=(K[1:]!=K[:-1])&A[1:]&A[:-1]; S[1:]|=c; S[:-1]|=c
c=(K[:,1:]!=K[:,:-1])&A[:,1:]&A[:,:-1]; S[:,1:]|=c; S[:,:-1]|=c
print('F201b grid',H.shape,'seam cells',int(S.sum()),flush=True)
# rev c: step-only lift. For each adjacent cell pair across a sheet change, slope-corrected step = H[n] - (H[c] + (H[c]-H[c-dir])).
# The LOW side's sheet gets lift L=step at its boundary cell, decaying exp(-d/0.6 m) into that sheet's own visible area (<= 2 m);
# its hidden verts under the high sheet within 0.6 m get the same lift but stay 1 mm under the high top (no coplanar faces).
import os
NX,NY=H.shape; LAM=float(os.environ.get('LAM','1.2')); CAPS=0.04
P=np.zeros((nS,NX,NY))
nst=0
for (di,dj) in ((1,0),(-1,0),(0,1),(0,-1)):
    for i in range(2,NX-2):
        for j in range(2,NY-2):
            k=K[i,j]
            if k<0 or k>=nS: continue
            kn=K[i+di,j+dj]
            if kn==k or kn<0 or kn>=nS: continue
            if K[i-di,j-dj]!=k: continue
            st=H[i+di,j+dj]-(2*H[i,j]-H[i-di,j-dj])
            if 0.002<st<0.06: P[k,i,j]=max(P[k,i,j],min(st,CAPS)); nst+=1
kf=math.exp(-ST/LAM)
for k in range(nS):
    M=(K==k)
    for it in range(int(2.5*LAM/ST)):
        p=np.pad(P[k],1); nb=np.maximum.reduce([p[:-2,1:-1],p[2:,1:-1],p[1:-1,:-2],p[1:-1,2:]])*kf
        P[k]=np.where(M,np.maximum(P[k],nb),0)
E=np.zeros_like(P)
for k in range(nS):
    E[k]=P[k].copy()
    for it in range(int(0.6/ST)):
        p=np.pad(E[k],1); nb=np.maximum.reduce([p[:-2,1:-1],p[2:,1:-1],p[1:-1,:-2],p[1:-1,2:]]); E[k]=np.maximum(E[k],nb)
np.savez('/workspace/nj-scenes/montclair-state/scripts/ws201/f201c_grid.npz',H=H,K=K,P=P.max(0),xs=xs,ys=ys)
print('F201b step pairs',nst,'lift cells>2mm',int((P.max(0)>0.002).sum()),'max',round(float(P.max()),3),flush=True)
def cell(x,y):
    i=int(round((x-X0)/ST)); j=int(round((y-Y0)/ST))
    return (i,j) if 0<=i<NX and 0<=j<NY else None
SK={o.name:k for k,o in enumerate(SH)}
tot=0;mx=0
for o in SH:
    k=SK[o.name]; mw=o.matrix_world; mi=mw.inverted(); n=0
    for v in o.data.vertices:
        p=mw@v.co; c=cell(p.x,p.y)
        if c is None: continue
        if K[c]==k: d=P[k][c]
        else:
            d=E[k][c]
            if d>0 and np.isfinite(H[c]): d=min(d,max(0.0,H[c]-0.001-p.z))
        if d>0.0005: p.z+=d; v.co=mi@p; n+=1; mx=max(mx,d)
    o.data.update(); tot+=n; print('F201b',o.name[:34],'lifted',n,flush=True)
PA=[o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith(('WS75','WS76','WS80','WS84','WS85')) and ('paint' in o.name.lower() or 'line' in o.name.lower()) and o not in SH]
PM=P.max(0); np2=0
for o in PA:
    mw=o.matrix_world; mi=mw.inverted()
    for v in o.data.vertices:
        p=mw@v.co; c=cell(p.x,p.y)
        if c is None: continue
        d=PM[c]
        if d>0.0005: p.z+=d; v.co=mi@p; np2+=1
    o.data.update()
print('F201b total sheet verts',tot,'max lift',round(mx,3),'paint verts',np2,flush=True)
del T,V,F
import gc; gc.collect()
