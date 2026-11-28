# ws268 (merge208 CHAIN, on main ws267c): UNIFY W72 — College Avenue + Lot 33 south of the police building (supersedes f268a/f268b,
# which lowered terrain verts: the terrain is re-snapped by its GN modifiers, so grade is fixed by raising paving only).
# Evidence: OSM College Avenue way 232850521 (centreline (-328,-37)->(-392,-21)), Lot 33 amenity=parking way 312848723,
# Carlisle Road 583841726 (W end); NJ 2020 ortho: one continuous paved area from the police walk (N curb ~y -21.5 at x -350,
# ~-20 at x -378) south through Lot 33. Main had no road or lot here: the ortho was draped on lumpy dtm_filled terrain (WS68 / M3b)
# with a hole (~x -357..-350, y -30..-50) where only the low 4 km skirt showed (dark notch).
# Build: ground sampled on the EVALUATED WS68 + M3b meshes (only their modifiers switched on), 1 m grid; paving z = robust quadratic
# fit (keeps the ~5% eastward rise) + a smoothed positive lift so the paving clears every ground sample by >= 3 cm (no lowering).
# Surface = one constrained Delaunay triangulation of the polygon (grid points + 0.7 m boundary samples, polygon as constraint),
# so it has no cracks; faces under the police walk / terrace / deck / Maintenance Building dropped; 0.6 m skirt down at the edges.
# Material = Roads_OSM's. Lane/stall markings, tree islands and curbs not modelled (UNVERIFIED).
import bpy, bmesh, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.geometry import delaunay_2d_cdt
TAG='P270A'; NAME='WS268_W72_CollegeAve_Lot33_paving_UNVERIFIED'

P=[(-336,-25.2),(-345,-23.0),(-355,-21.5),(-367,-20.6),(-378,-20.0),(-390,-19.5),(-390,-36),(-387,-39),(-376,-42),(-377,-46),
   (-327,-59),(-317,-61),(-315,-61),(-311,-48),(-318,-31),(-331,-27.2)]
def pip(x,y):
    c=False; n=len(P)
    for i in range(n):
        (x0,y0),(x1,y1)=P[i],P[(i+1)%n]
        if (y0>y)!=(y1>y) and x<x0+(y-y0)*(x1-x0)/(y1-y0): c=not c
    return c
def edist(x,y):
    d=1e9; n=len(P)
    for i in range(n):
        (x0,y0),(x1,y1)=P[i],P[(i+1)%n]; dx,dy=x1-x0,y1-y0; t=max(0,min(1,((x-x0)*dx+(y-y0)*dy)/(dx*dx+dy*dy)))
        d=min(d,((x-x0-t*dx)**2+(y-y0-t*dy)**2)**.5)
    return d
GN=('WS68_RHD_ground_northDTM','M3b_north_LiDAR_DTM_1m_west_rail_corridor_UNVERIFIED_seam')
gobs=[o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith(GN)]
for o in gobs:
    for m in o.modifiers: m.show_viewport=True
dg=bpy.context.evaluated_depsgraph_get()
def tree(o,me,margin=2):
    bm=bmesh.new(); bm.from_mesh(me); bm.transform(o.matrix_world)
    dl=[f for f in bm.faces if not any(-393-margin<v.co.x<-308+margin and -64-margin<v.co.y<-17+margin for v in f.verts)]
    bmesh.ops.delete(bm,geom=dl,context='FACES'); t=BVHTree.FromBMesh(bm); bm.free(); return t
GT=[]
for o in gobs:
    oe=o.evaluated_get(dg); me=oe.to_mesh(); GT.append(tree(o,me)); oe.to_mesh_clear()
for o in gobs:
    for m in o.modifiers: m.show_viewport=False
print(TAG,'ground (evaluated)',[o.name[:40] for o in gobs],flush=True)
BLK=[o for o in bpy.data.objects if o.type=='MESH' and (o.name in ('ge_police_south_walk','ge_police_terrace_walls','ge_police_terrace_bed','Red Hawk Deck') or o.name.startswith(('Red Hawk W core','MSU Maintenance Building')))]
BT=[tree(o,o.data,5) for o in BLK]
def gz(x,y):
    b=None
    for t in GT:
        r=t.ray_cast(Vector((x,y,200)),Vector((0,0,-1)))
        if r[0] is not None and (b is None or r[0].z>b): b=r[0].z
    return b
def blocked(x,y):  # a blocker mesh directly above/below ground level here (walk, terrace, deck ground floor, maintenance bldg)
    for t in BT:
        r=t.ray_cast(Vector((x,y,135)),Vector((0,0,-1)))
        if r[0] is not None and r[0].z<134: return True
    return False
X=np.arange(-393,-307,1.0); Y=np.arange(-64,-16,1.0)
Z=np.full((len(Y),len(X)),np.nan)
for i,y in enumerate(Y):
    for j,x in enumerate(X):
        if edist(x,y)<2.5 or pip(x,y):
            z=gz(x,y); Z[i,j]=np.nan if z is None else z
gx,gy=np.meshgrid(X,Y); ok=~np.isnan(Z)
def basis(x,y): x=(x+350)/40; y=(y+35)/20; return np.stack([np.ones_like(x),x,y,x*x,x*y,y*y],-1)
A=np.c_[gx[ok],gy[ok],Z[ok]]; keep=np.ones(len(A),bool)
for it in range(4):
    c,*_=np.linalg.lstsq(basis(A[keep,0],A[keep,1]),A[keep,2],rcond=None); res=A[:,2]-basis(A[:,0],A[:,1])@c
    keep=np.abs(res)<max(0.25,2.5*np.std(res[keep]))
print(TAG,'fit',c.round(3),'res p5/p50/p95',np.percentile(res,[5,50,95]).round(2),'max',res.max().round(2),'min',res.min().round(2),flush=True)
F=basis(gx,gy)@c; R=np.where(ok,Z-F,0.0); Rp=np.maximum(R,0)
def maxf(a,k):
    o=a.copy()
    for di in range(-k,k+1):
        for dj in range(-k,k+1): o=np.maximum(o,np.roll(np.roll(a,di,0),dj,1))
    return o
def gauss(a,s):
    k=int(3*s); w=np.exp(-0.5*(np.arange(-k,k+1)/s)**2); w/=w.sum()
    a=np.apply_along_axis(lambda r: np.convolve(np.pad(r,k,mode='edge'),w,'valid'),1,a)
    return np.apply_along_axis(lambda r: np.convolve(np.pad(r,k,mode='edge'),w,'valid'),0,a)
L=np.maximum(gauss(maxf(Rp,2),1.5),maxf(Rp,1))   # smoothed lift, never below the 3x3 local max
S=F+L+0.04

import json
pav=bpy.data.objects[NAME]
bmo=bmesh.new(); bmo.from_mesh(pav.data); bmo.transform(pav.matrix_world); TPo=BVHTree.FromBMesh(bmo); bmo.free()
PZ=np.full_like(Z,np.nan)
for i,y in enumerate(Y):
    for j,x in enumerate(X):
        r=TPo.ray_cast(Vector((x,y,200)),Vector((0,0,-1)))
        if r[0] is not None: PZ[i,j]=r[0].z
inside=np.array([[pip(x,y) for x in X] for y in Y])
np.savez('/workspace/nj-scenes/montclair-state/scripts/ws270/probe270a.npz',X=X,Y=Y,Z=Z,F=F,L=L,S=S,PZ=PZ,inside=inside,c=c,P=np.array(P))
print(TAG,'saved npz; old paving vs S max diff',np.nanmax(np.abs(PZ-S)).round(3),flush=True)
raise SystemExit(0)
