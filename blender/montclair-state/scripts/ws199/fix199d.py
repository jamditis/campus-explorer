# ws199 W17: light band across the near aisle in the W eye view (pre-existing, also in ws197c) = N-S step in WS76 at x~-249.1
# (W side ~4.4 cm low vs the E slope extended; 0.6 m strip at ~13% vs 6% lot slope catches the low sun). RAISE-ONLY:
# W side lifted toward the E-side slope line, smoothstep taper to 0 at x=-253.5. Paint/underlay follow upward deltas.
import bpy, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
XS,XA,XE2=-249.1,-253.5,-247.6   # step line, taper end (W), E fit point
YB0,YB1=-86.0,-66.0
AS=['WS75_sprague_lot_asphalt_ortho2020_UNVERIFIED_edges','WS76_accessible_lot_asphalt_ortho2020_UNVERIFIED_edges','WS94_lot_slit_filler_asphalt_UNVERIFIED']
def bvh(names):
    V=[];F=[]
    for n in names:
        o=bpy.data.objects[n]; mw=o.matrix_world; b=len(V)
        V+=[mw@v.co for v in o.data.vertices]; F+=[tuple(b+i for i in p.vertices) for p in o.data.polygons]
    return BVHTree.FromPolygons(V,F)
OLD=bvh(AS)
def zt(T,x,y):
    h=T.ray_cast(Vector((x,y,300)),Vector((0,0,-1))); return h[0].z if h[0] else None
cache={}
def eline(y):
    k=round(y,1)
    if k not in cache:
        a=zt(OLD,XE2,k); b=zt(OLD,XE2+1.0,k); cache[k]=None if (a is None or b is None) else (a,b-a)
    return cache[k]
def target(x,y,z):
    if not (XA<x<XS+0.05 and YB0<y<YB1): return 0.0
    e=eline(y)
    if e is None: return 0.0
    a,s=e; s=min(max(s,0.03),0.09); ze=a+s*(x-XE2)
    t=(x-XA)/(XS-XA); w=t*t*(3-2*t)
    return min(0.07,max(0.0,w*(ze-z)))
st={}
for n in AS:
    o=bpy.data.objects[n]; mw=o.matrix_world; mi=mw.inverted(); k=0; dm=0
    for v in o.data.vertices:
        w=mw@v.co
        if not (XA<w.x<XS+0.05): continue
        z0=zt(OLD,w.x,w.y)
        if z0 is None or w.z<z0-0.03: continue
        dz=target(w.x,w.y,w.z)
        if dz>0: w.z+=dz; v.co=mi@w; k+=1; dm=max(dm,dz)
    o.data.update(); st[n[:6]]=(k,round(dm,3))
print('F199d moved',st,flush=True)
NEW=bvh(AS); pk={}
for o in bpy.data.objects:
    if o.type!='MESH' or o.name in AS or not any(t in o.name for t in ('paint','ISA','stall','underlay','filler')): continue
    bb=[o.matrix_world@Vector(q) for q in o.bound_box]
    if max(b.x for b in bb)<XA or min(b.x for b in bb)>XS+0.1 or max(b.y for b in bb)<YB0 or min(b.y for b in bb)>YB1: continue
    mw=o.matrix_world; mi=mw.inverted(); k=0
    for v in o.data.vertices:
        w=mw@v.co
        if not (XA<w.x<XS+0.1): continue
        zo=zt(OLD,w.x,w.y); zn=zt(NEW,w.x,w.y)
        if zo is None or zn is None or abs(w.z-zo)>0.08 or zn<=zo: continue
        w.z+=zn-zo; v.co=mi@w; k+=1
    o.data.update(); pk[o.name[:12]]=k
print('F199d follow',pk,flush=True)
for y in (-79,-76,-73,-71):
    zs=[zt(NEW,x,y) for x in np.arange(-254,-246,0.3)]
    if all(zs): print('F199d slope%% y%d'%y,' '.join('%.0f'%(v*100/0.3) for v in np.diff(zs)),flush=True)
