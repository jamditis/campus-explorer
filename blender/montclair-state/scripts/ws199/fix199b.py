# rev2 00:37 ET
# ws199 W16b: ISA3 (row B 2nd/3rd square, centre (-237.8,-80.7)) fold = N-S WS75/WS76 seam at x~-238.6 (WS76 tongue 1.5-4 cm proud)
# Designer call: accessible stalls are a single planar ADA slab (<=2% cross slope), so re-grade WS75/WS76/WS94 top to ONE fitted plane,
# lifted to its upper envelope (95th pct residual) => RAISE-ONLY (terrain GN re-snaps LiDAR; never lower). 1.5 m feather. Paint follows.
import bpy, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
CX0,CX1,CY0,CY1,FB=-246.0,-235.0,-81.9,-78.6,1.5  # rev2: core widened W over squares 1-3 (dip at (-243,-80))
AS=['WS75_sprague_lot_asphalt_ortho2020_UNVERIFIED_edges','WS76_accessible_lot_asphalt_ortho2020_UNVERIFIED_edges','WS94_lot_slit_filler_asphalt_UNVERIFIED']
def wt(x,y):
    d=max(CX0-x,0,x-CX1,CY0-y,0,y-CY1); return 1.0 if d<=0 else max(0.0,1-d/FB)
def bvh(names):
    V=[];F=[]
    for n in names:
        o=bpy.data.objects[n]; mw=o.matrix_world; b=len(V)
        V+=[mw@v.co for v in o.data.vertices]; F+=[tuple(b+i for i in p.vertices) for p in o.data.polygons]
    return BVHTree.FromPolygons(V,F)
OLD=bvh(AS)
def zt(T,x,y):
    h=T.ray_cast(Vector((x,y,300)),Vector((0,0,-1))); return h[0].z if h[0] else None
P=[]
for x in np.arange(CX0,CX1,0.1):
    for y in np.arange(CY0,CY1,0.1):
        z=zt(OLD,x,y)
        if z is not None: P.append((x,y,z))
P=np.array(P); A=np.c_[np.ones(len(P)),P[:,0]+238,P[:,1]+80.5]
c=np.linalg.lstsq(A,P[:,2],rcond=None)[0]; r=P[:,2]-A@c; off=float(np.percentile(r,95))
print('F199b plane slope x %.4f y %.4f rms %.3f max %.3f off %.3f'%(c[1],c[2],np.sqrt((r**2).mean()),r.max(),off),flush=True)
def pl(x,y): return c[0]+c[1]*(x+238)+c[2]*(y+80.5)+off
st={}
for n in AS:
    o=bpy.data.objects[n]; mw=o.matrix_world; mi=mw.inverted(); k=0; dm=0
    for v in o.data.vertices:
        w=mw@v.co; a=wt(w.x,w.y)
        if a<=0: continue
        z0=zt(OLD,w.x,w.y)
        if z0 is None or w.z<z0-0.03: continue
        dz=min(0.06,max(0.0,a*(pl(w.x,w.y)-w.z)))
        if dz>0: w.z+=dz; v.co=mi@w; k+=1; dm=max(dm,dz)
    o.data.update(); st[n[:6]]=(k,round(dm,3))
print('F199b moved',st,flush=True)
NEW=bvh(AS); pk={}
for o in bpy.data.objects:
    if o.type!='MESH' or o.name in AS or not any(t in o.name for t in ('paint','ISA','stall','underlay')): continue
    bb=[o.matrix_world@Vector(q) for q in o.bound_box]
    if max(b.x for b in bb)<CX0-FB or min(b.x for b in bb)>CX1+FB or max(b.y for b in bb)<CY0-FB or min(b.y for b in bb)>CY1+FB: continue
    mw=o.matrix_world; mi=mw.inverted(); k=0
    for v in o.data.vertices:
        w=mw@v.co
        if wt(w.x,w.y)<=0: continue
        zo=zt(OLD,w.x,w.y); zn=zt(NEW,w.x,w.y)
        if zo is None and 'underlay' in o.name and wt(w.x,w.y)>=1:
            t=pl(w.x,w.y)-0.004
            if t-0.10<w.z<t: w.z=t; v.co=mi@w; k+=1  # rev2: hole under an AS gap -> lift underlay flush (raise-only)
            continue
        if zo is None or zn is None or abs(w.z-zo)>0.08 or zn<=zo: continue
        w.z+=zn-zo; v.co=mi@w; k+=1
    o.data.update(); pk[o.name[:10]]=k
print('F199b paint/underlay follow',pk,flush=True)
mx=0
for y in np.arange(CY0,CY1,0.25):
    zs=[zt(NEW,x,y) for x in np.arange(CX0,CX1,0.2)]; zs=[z for z in zs if z]
    d=np.diff(np.diff(zs)); mx=max(mx,float(np.abs(d).max()))
print('F199b max 2nd diff along x (0.2 m)',round(mx,3),flush=True)
