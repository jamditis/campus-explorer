# ws198: Red Hawk/Kasser accessible lot — WS75/WS76 seam crease + WS94 slit-filler wedge (light, tilted filler facets nz 0.75-0.96).
# ws198 rev3 (final): zone narrowed to the seam band y[-84,-77] (2.5 m feather); only TOP-layer verts (within 3 cm of the old top surface) sampled/moved — slab-bottom/skirt verts untouched.
# Designer call: one continuous lot slab across the WS75/WS76 seam (ortho 2020: uninterrupted asphalt, no joint/gutter visible).
# Re-grade WS75+WS76+WS94 verts in x[-240,-214] y[-88,-70] to a moving-least-squares plane (Gaussian r=3 m) of the LiDAR-draped
# lot asphalt away from the seam band (|y+80.5|>1.5), outliers (curb/edge verts, |r|>0.12 vs coarse quadratic) excluded & never moved.
# Weight tapers 3 m outside the zone and 2 m from the outer lot boundary (curb lines frozen). Paint/ISA/stall get the same delta.
import bpy, bmesh, numpy as np
from mathutils import Vector, kdtree
from mathutils.bvhtree import BVHTree
DN=0.0  # ws198 RAISE-ONLY variant (fix198r): never lower (terrain GN would show through); seam-band samples included so the ridge lifts the plane; rev6: max lowering 5 cm — the terrain GN stack (WS78/QM band_to_DTM) re-snaps LiDAR grass above a deeper cut
X0,X1,Y0,Y1,FE=-240.0,-214.0,-84.0,-77.0,2.5
AS=['WS75_sprague_lot_asphalt_ortho2020_UNVERIFIED_edges','WS76_accessible_lot_asphalt_ortho2020_UNVERIFIED_edges','WS94_lot_slit_filler_asphalt_UNVERIFIED']
def wz(x,y):
    dx=max(X0-x,0,x-X1); dy=max(Y0-y,0,y-Y1); d=max(dx,dy)
    return 1.0 if d<=0 else max(0.0,1-d/FE)
def bvh(names):
    V=[];F=[]
    for n in names:
        o=bpy.data.objects[n]; mw=o.matrix_world; b=len(V)
        V+= [mw@v.co for v in o.data.vertices]; F+=[tuple(b+i for i in p.vertices) for p in o.data.polygons]
    return BVHTree.FromPolygons(V,F)
OLD=bvh(AS)
def ztop(T,x,y):
    h=T.ray_cast(Vector((x,y,300)),Vector((0,0,-1))); return h[0].z if h[0] else None
P=[]; BND=[]
for n in AS:
    o=bpy.data.objects[n]; mw=o.matrix_world
    bm=bmesh.new(); bm.from_mesh(o.data)
    for v in bm.verts:
        w=mw@v.co
        if not (X0-FE-3<w.x<X1+FE+3 and Y0-FE-3<w.y<Y1+FE+3): continue
        isb=any(e.is_boundary for e in v.link_edges)
        if isb and n!=AS[2] and abs(w.y+80.5)>2.0: BND.append(w.copy())
        zt_=ztop(OLD,w.x,w.y)
        if n!=AS[2] and abs(w.y+80.5)>-1 and not isb and zt_ is not None and w.z>zt_-0.03: P.append((w.x,w.y,w.z))
    bm.free()
P=np.array(P); mx,my=-227.0,-79.0
def A(x,y): x=x-mx; y=y-my; return np.stack([np.ones_like(x),x,y,x*x,x*y,y*y],-1)
keep=np.ones(len(P),bool)
for it in range(4):
    c,*_=np.linalg.lstsq(A(P[keep,0],P[keep,1]),P[keep,2],rcond=None)
    r=P[:,2]-A(P[:,0],P[:,1])@c; keep=np.abs(r)<0.12
P=P[keep]; print('F198 samples',len(P),'coarse rms',round(float(np.sqrt(np.mean(r[keep]**2))),3),flush=True)
kb=kdtree.KDTree(len(BND))
for i,b in enumerate(BND): kb.insert((b.x,b.y,0),i)
kb.balance()
def mls(x,y):
    d2=(P[:,0]-x)**2+(P[:,1]-y)**2; w=np.exp(-d2/(2*2.5**2)); m=w>1e-3
    Q=np.stack([np.ones(m.sum()),P[m,0]-x,P[m,1]-y],-1); W=w[m]
    cc=np.linalg.lstsq(Q*W[:,None]**.5,P[m,2]*W**.5,rcond=None)[0]; return float(cc[0])
def weight(x,y):
    w=wz(x,y)
    if w<=0: return 0
    if len(BND): _,_,d=kb.find((x,y,0)); w*=min(1.0,d/2.0)
    return w
st={}
for n in AS:
    o=bpy.data.objects[n]; me=o.data; mw=o.matrix_world; mi=mw.inverted(); k=0; dmax=0; skip=0
    for v in me.vertices:
        w=mw@v.co; a=weight(w.x,w.y)
        if a<=0: continue
        t=mls(w.x,w.y); dz=a*(t-w.z)
        zt_=ztop(OLD,w.x,w.y)
        if zt_ is None or w.z<zt_-0.03 or abs(t-w.z)>0.3: skip+=1; continue
        dz=max(-DN,min(0.12,dz)); w.z+=dz; v.co=mi@w; k+=1; dmax=max(dmax,abs(dz))
    me.update(); st[n]=(k,skip,round(dmax,3))
print('F198 asphalt moved,skipped,maxdz',st,flush=True)
NEW=bvh(AS)
pk={}
for o in bpy.data.objects:
    if o.type!='MESH' or o.name in AS: continue
    if not any(t in o.name for t in ('paint','ISA','stall','zebra')): continue
    bb=[o.matrix_world@Vector(cc) for cc in o.bound_box]
    if max(b.x for b in bb)<X0-FE or min(b.x for b in bb)>X1+FE or max(b.y for b in bb)<Y0-FE or min(b.y for b in bb)>Y1+FE: continue
    mw=o.matrix_world; mi=mw.inverted(); k=0
    for v in o.data.vertices:
        w=mw@v.co
        if wz(w.x,w.y)<=0: continue
        zo=ztop(OLD,w.x,w.y); zn=ztop(NEW,w.x,w.y)
        if zo is None or zn is None or abs(w.z-zo)>0.08: continue
        w.z+=zn-zo; v.co=mi@w; k+=1
    o.data.update(); pk[o.name]=k
print('F198 paint',pk,flush=True)
Tn=bpy.data.objects['Terrain_LiDAR_DTM_1m']; mw=Tn.matrix_world; mi=mw.inverted(); tf=0
for v in Tn.data.vertices:
    w=mw@v.co
    if X0-FE<w.x<X1+FE and Y0-FE<w.y<Y1+FE:
        za=ztop(NEW,w.x,w.y)
        if za is not None and w.z>za-0.05:
            w.z=za-0.07; v.co=mi@w; tf+=1
            if Tn.data.shape_keys:
                for kb_ in Tn.data.shape_keys.key_blocks: kb_.data[v.index].co=mi@w
Tn.data.update(); print('F198 terrain lowered',tf,flush=True)
for n in AS:
    o=bpy.data.objects[n]; mw=o.matrix_world; bad=0; tot=0
    for p in o.data.polygons:
        cc=mw@p.center
        if wz(cc.x,cc.y)>=1 and -84<cc.y<-77.5: tot+=1; bad+= (mw.to_3x3()@p.normal).normalized().z<0.985
    print('F198 tilted faces in seam band',n,bad,'/',tot,flush=True)
# seam step check
mx_=0
for x in np.arange(-238,-214,0.5):
    zs=[ztop(NEW,x,y) for y in np.arange(-82,-79,0.25)]; zs=[z for z in zs if z is not None]
    if len(zs)>2: mx_=max(mx_,max(abs(zs[i+1]-zs[i]) for i in range(len(zs)-1)))
print('F198 max 25cm step across seam',round(mx_,3),flush=True)
# rev5 (final): under-layers poke-through after the re-grade. Only Roads_OSM + WS81 seam underlay + WS96 filler, only where the
# re-graded AS top exists and the under-layer is above it (core zone only, wz==1) -> 3 cm under. (rev4/4b moved WS81 everywhere in
# the zone and exposed LiDAR grass — WS81 is the visible cover over terrain outside the AS top; left untouched there.)
UL={}
for o in bpy.data.objects:
    if o.type!='MESH' or o.name in AS or o.hide_render: continue
    if not (o.name=='Roads_OSM' or 'underlay' in o.name or 'filler' in o.name): continue
    bb=[o.matrix_world@Vector(cc) for cc in o.bound_box]
    if max(b.x for b in bb)<X0 or min(b.x for b in bb)>X1 or max(b.y for b in bb)<Y0 or min(b.y for b in bb)>Y1: continue
    mw=o.matrix_world; mi=mw.inverted(); k=0
    for v in o.data.vertices:
        w=mw@v.co
        if wz(w.x,w.y)<1: continue
        zn=ztop(NEW,w.x,w.y)
        zo=ztop(OLD,w.x,w.y)
        if o.name=='Roads_OSM':
            if zn is not None and zn-0.5<w.z>zn-0.01: w.z=zn-0.03; v.co=mi@w; k+=1
        elif zn is not None and zo is not None and abs(w.z-zo)<0.03 and zn>zo: w.z+=zn-zo; v.co=mi@w; k+=1  # raise-only follow
        pass  # rev7: WS81/WS96 left untouched (moving them exposes GN-snapped LiDAR grass)
    o.data.update(); UL[o.name]=k
print('F198 underlays pushed (core only)',UL,flush=True)
# rev4c: WS81 underlay is the visible top where WS75/WS76 have gaps; after it followed the re-grade, LiDAR terrain poked through
# (object-ID render 2342). Lower terrain 7 cm under the combined lot top (AS + WS81 + WS96) inside the zone.
NEW2=bvh(AS+[n for n in UL if n!='Roads_OSM'])
Tn=bpy.data.objects['Terrain_LiDAR_DTM_1m']; mw=Tn.matrix_world; mi=mw.inverted(); tf=0
for v in Tn.data.vertices:
    w=mw@v.co
    if X0-FE-1<w.x<X1+FE+1 and Y0-FE-1<w.y<Y1+FE+1:
        za=ztop(NEW2,w.x,w.y)
        if za is not None and w.z>za-0.05:
            w.z=za-0.07; v.co=mi@w; tf+=1
            if Tn.data.shape_keys:
                for kb_ in Tn.data.shape_keys.key_blocks: kb_.data[v.index].co=mi@w
print('F198 terrain shape keys',[k.name for k in Tn.data.shape_keys.key_blocks] if Tn.data.shape_keys else None, 'mods',[m.name+':'+m.type for m in Tn.modifiers]); Tn.data.update(); print('F198 terrain lowered under lot+underlay',tf,flush=True)
