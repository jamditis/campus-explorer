# ws200 W18: soft bumps/dips in the Sprague-lot asphalt S of the WS77 median (WS75 + WS80 fill), seen in the ws199 oblique.
# Probe p200d (0.25 m top grid, real GN terrain): region x -263..-216, y -107..-95.5 is near-planar (plane rms 2.6 cm) with dips to -7 cm
# and 1-10 cm steps on the wavy WS75/WS80 seam. Designer call: a surface lot is graded as one smooth warped plane draining to its low edge
# (2020 ortho: uninterrupted asphalt, no gutters/inlets visible in this bay -> UNVERIFIED). RAISE-ONLY (never lower lot paving: terrain GN
# re-snaps to the DTM): z -> max(z, Q) with Q a robust quadratic fit, lift capped 7 cm, feathered to 0 over 1.2 m at the region edges;
# paint on the lot follows the same delta (stays flush).
# rev2 (1:39 AM): rev1 lifted each vertex by its OWN deficit -> WS75/WS80 overlap seam opened into dark cracks in the oblique.
# Now ONE delta field from the ORIGINAL top surface is applied to every lot sheet + underlays (WS75, WS80, WS81, WS82, WS83 skin, WS94, WS96) so
# their relative stacking is unchanged (no new gaps), only the whole bay is lifted onto the smooth grade.
import bpy, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
RX0,RX1,RY0,RY1,FE,CAP=-263.0,-216.0,-107.0,-95.5,1.2,0.07
AS2=[o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith(('WS75_sprague_lot_asphalt','WS80_sprague_lot_fill_asphalt'))]
V=[];F=[]
for o in AS2:
    mw=o.matrix_world; b=len(V); V+=[mw@v.co for v in o.data.vertices]; F+=[tuple(b+i for i in p.vertices) for p in o.data.polygons]
TA=BVHTree.FromPolygons(V,F)
def za(x,y):
    h=TA.ray_cast(Vector((x,y,300)),Vector((0,0,-1))); return h[0].z if h[0] else None
def zn(x,y,z):
    h=za(x,y)
    if h is not None: return h
    loc=TA.find_nearest(Vector((x,y,z)),1.0)[0]; return loc.z if loc else None
pts=[(x,y,za(x,y)) for x in np.arange(RX0+0.5,RX1,0.5) for y in np.arange(RY0+0.5,RY1,0.5)]
P=np.array([p for p in pts if p[2] is not None])
def basis(x,y): x=(np.asarray(x)+240)/20; y=(np.asarray(y)+100)/6; return np.stack([np.ones_like(x),x,y,x*x,x*y,y*y],-1)
keep=np.ones(len(P),bool)
for it in range(4):
    c=np.linalg.lstsq(basis(P[keep,0],P[keep,1]),P[keep,2],rcond=None)[0]; r=P[:,2]-basis(P[:,0],P[:,1])@c
    keep=np.abs(r-np.median(r[keep]))<max(0.05,2.5*r[keep].std())
print('F200b fit n',keep.sum(),'/',len(P),'rms',round(float(r[keep].std()),3),'dip<-3cm',int((r<-0.03).sum()),'hump>3cm',int((r>0.03).sum()),flush=True)
def w(x,y):
    d=min(x-RX0,RX1-x,y-RY0,RY1-y)
    if d<=0: return 0.0
    t=min(d/FE,1.0); return t*t*(3-2*t)
def dl(x,y,z0):
    ww=w(x,y)
    if ww==0 or z0 is None: return 0.0
    q=float(basis(x,y)@c); return min(max(q-z0,0.0),CAP)*ww
mx=0;n=0
FOL=[o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith(('WS81_lot_seam_underlay','WS82_sprague_lane_onesurface','WS83_lane_gutter_skin','WS94_lot_slit_filler','WS96_lot_E_edge_gap_filler'))]
for o in AS2+FOL:
    mw=o.matrix_world; mi=mw.inverted()
    for v in o.data.vertices:
        p=mw@v.co; d=dl(p.x,p.y,zn(p.x,p.y,p.z))
        if d>0: p.z+=d; v.co=mi@p; n+=1; mx=max(mx,d)
    o.data.update()
PA=[o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith(('WS75','WS80','WS84','WS85')) and ('paint' in o.name.lower() or 'line' in o.name.lower()) and o not in AS2 and o not in FOL]
np2=0
for o in PA:
    mw=o.matrix_world; mi=mw.inverted()
    for v in o.data.vertices:
        p=mw@v.co; d=dl(p.x,p.y,za(p.x,p.y))
        if d>0: p.z+=d; v.co=mi@p; np2+=1
    o.data.update()
print('F200b lifted',n,'asphalt verts max',round(mx,3),'paint verts',np2,[o.name[:30] for o in PA],flush=True)
