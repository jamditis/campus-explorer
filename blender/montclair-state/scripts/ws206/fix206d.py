# ws206 W19 leftover: WS94 lot slit filler stands 2-9 mm PROUD of the WS75/WS80/WS81 lot asphalt it overlaps (ws203 probe),
# drawing two faint marks near x -233.3 (y -105.6 / -99.5). Tuck: every WS94 vertex that overlaps a neighbouring lot sheet is set
# to (neighbour top - 2 mm) when higher; verts in the bare slit (no neighbour) are blended toward the tucked neighbours over
# 0.5 m only if they are proud of the local neighbour plane. Lower-only on the filler; neighbours untouched.
import bpy, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
def obs(p): return [o for o in bpy.data.objects if o.name.startswith(p)]
def bvh(o):
    mw=o.matrix_world; return BVHTree.FromPolygons([mw@v.co for v in o.data.vertices],[tuple(p.vertices) for p in o.data.polygons])
def hz(t,x,y):
    h=t.ray_cast(Vector((x,y,160)),Vector((0,0,-1)),80); return h[0].z if h[0] is not None else None
F=obs('WS94_lot_slit_filler')[0]
NB=[o for p in ('WS75_sprague_lot_asphalt','WS80_sprague_lot_fill') for o in obs(p) if o.type=='MESH' and len(o.data.polygons)]
print('F206d neighbours',[o.name[:30] for o in NB],flush=True)
NT=[bvh(o) for o in NB]
mw=F.matrix_world; mi=mw.inverted(); P=np.array([tuple(mw@v.co) for v in F.data.vertices]); NZ=P[:,2].copy()
print('F206d filler verts',len(P),'bbox',np.round(P.min(0),2),np.round(P.max(0),2),flush=True)
ov=np.zeros(len(P),bool); pr=[]
for k,p in enumerate(P):
    zs=[hz(t,p[0],p[1]) for t in NT]; zs=[z for z in zs if z is not None and abs(z-p[2])<0.05]
    if zs:
        ov[k]=True; c=max(zs)-0.002
        if p[2]>c: pr.append(p[2]-c); NZ[k]=c
print('F206d overlap verts',ov.sum(),'proud',len(pr),'max %.4f'%(max(pr) if pr else 0),flush=True)
# blend free verts: limit to <= nearest tucked overlap vert + slope continuity (drop proud bumps)
D=NZ-P[:,2]; idx=np.where(D<0)[0]; nf=0
for k in np.where(~ov)[0]:
    if len(idx)==0: break
    d=np.sqrt(((P[idx,:2]-P[k,:2])**2).sum(1)); f=np.clip(1-d/0.5,0,1)
    dz=float((D[idx]*f).min())
    if dz<0: NZ[k]=P[k,2]+dz; nf+=1
for k,v in enumerate(F.data.vertices):
    g=mw@v.co; g.z=NZ[k]; v.co=mi@g
F.data.update(); print('F206d free verts blended',nf,flush=True)
