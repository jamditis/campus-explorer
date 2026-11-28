# ws268 (merge208 CHAIN, on ws268a): W72 edge feather. Outside the paving polygon the dtm_filled terrain stands up to ~0.5 m
# above the new paving in lumps along the W (Carlisle side), Lot 33 S/W and E edges. Lower-only feather of the terrain base verts
# within 4 m of those edges toward the same paving fit - 8 cm (blend by distance), so the ground meets the paving edge instead of
# humping over it. N/E edges along the police walk / terrace / deck are not touched (real grade up to the walk). Fit recomputed
# from the ORIGINAL ground is not possible on ws268a (verts already lowered inside) -> refit on samples outside the 0.5 m inset only.
import bpy, bmesh, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
TAG='F268B'
P=[(-336,-25.2),(-345,-23.0),(-355,-21.5),(-367,-20.6),(-378,-20.0),(-390,-19.5),(-390,-36),(-387,-39),(-376,-42),(-377,-46),
   (-327,-59),(-317,-61),(-315,-61),(-311,-48),(-318,-31),(-331,-27.2)]
def pip(x,y,P=P):
    c=False; n=len(P)
    for i in range(n):
        (x0,y0),(x1,y1)=P[i],P[(i+1)%n]
        if (y0>y)!=(y1>y) and x<x0+(y-y0)*(x1-x0)/(y1-y0): c=not c
    return c
def edist(x,y,P=P):
    d=1e9; n=len(P)
    for i in range(n):
        (x0,y0),(x1,y1)=P[i],P[(i+1)%n]; dx,dy=x1-x0,y1-y0; t=max(0,min(1,((x-x0)*dx+(y-y0)*dy)/(dx*dx+dy*dy)))
        d=min(d,((x-x0-t*dx)**2+(y-y0-t*dy)**2)**.5)
    return d
class _P:
    contains_point=staticmethod(lambda p: pip(*p))
poly=_P()
def tree(o,margin=2):
    bm=bmesh.new(); bm.from_mesh(o.data); bm.transform(o.matrix_world)
    dl=[f for f in bm.faces if not any(-393-margin<v.co.x<-308+margin and -64-margin<v.co.y<-17+margin for v in f.verts)]
    bmesh.ops.delete(bm,geom=dl,context='FACES'); t=BVHTree.FromBMesh(bm); bm.free(); return t
GN=['WS68_RHD_ground_northDTM','M3b_north_LiDAR_DTM_1m_west_rail_corridor_UNVERIFIED_seam']
gobs=[o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith(tuple(GN))]
print(TAG,'ground',[o.name[:40] for o in gobs],flush=True)
GT=[tree(o) for o in gobs]
BLK=[o for o in bpy.data.objects if o.type=='MESH' and (o.name in ('ge_police_south_walk','ge_police_terrace_walls','ge_police_terrace_bed','Red Hawk Deck') or o.name.startswith(('Red Hawk W core','MSU Maintenance Building')))]
BT=[(o.name[:30],tree(o,5)) for o in BLK]
def gz(x,y):
    b=None
    for t in GT:
        r=t.ray_cast(Vector((x,y,200)),Vector((0,0,-1)))
        if r[0] is not None and (b is None or r[0].z>b): b=r[0].z
    return b
def blocked(x,y,z):
    for n,t in BT:
        for d in ((0,0,1),(0,0,-1)):
            r=t.ray_cast(Vector((x,y,z-3 if d[2]>0 else z+30)),Vector(d))
            if r[0] is not None and (n.startswith(('ge_police','Red Hawk','MSU')) ): return n
    return None
xs=np.arange(-391,-309,1.0); ys=np.arange(-62,-18,1.0)
S=[(x,y,gz(x,y)) for x in xs for y in ys if poly.contains_point((x,y))]
A=np.array([s for s in S if s[2] is not None]); print(TAG,'samples',len(S),'hits',len(A),flush=True)
def basis(x,y): x=(x+350)/40; y=(y+35)/20; return np.stack([np.ones_like(x),x,y,x*x,x*y,y*y],-1)
keep=np.ones(len(A),bool)
for it in range(4):
    c,*_=np.linalg.lstsq(basis(A[keep,0],A[keep,1]),A[keep,2],rcond=None); res=A[:,2]-basis(A[:,0],A[:,1])@c
    keep=np.abs(res)<max(0.25,2.5*np.std(res[keep]))
print(TAG,'fit',c.round(3),'res p5/p50/p95',np.percentile(res,[5,50,95]).round(2),'max',res.max().round(2),'min',res.min().round(2),flush=True)
c=np.array([119.745,2.383,0.266,0.697,0.684,0.35])  # f268a coefficients (ws267c ground; printed 3 dp, <1 cm)
fz=lambda x,y: float(basis(np.array(x),np.array(y))@c)

if bpy.data.objects.get('WS268_W72_CollegeAve_Lot33_paving_UNVERIFIED') is None: raise SystemExit('F268B needs f268a')
pv=bpy.data.objects['WS268_W72_CollegeAve_Lot33_paving_UNVERIFIED']
if pv.get('ws268b'): raise SystemExit('F268B already applied')
# use the paving mesh itself as the target surface (exact edge z), extrapolated by nearest-edge for verts outside
pz=np.array([(pv.matrix_world@v.co)[:] for v in pv.data.vertices]); top=pz[pz[:,2]>=np.percentile(pz[:,2],0)]
def edist_i(x,y):
    best=(1e9,-1); n=len(P)
    for i in range(n):
        (x0,y0),(x1,y1)=P[i],P[(i+1)%n]; dx,dy=x1-x0,y1-y0; t=max(0,min(1,((x-x0)*dx+(y-y0)*dy)/(dx*dx+dy*dy)))
        d=((x-x0-t*dx)**2+(y-y0-t*dy)**2)**.5
        if d<best[0]: best=(d,i)
    return best
FE=set(range(5,14))  # edges (-390,-19.5)->(-390,-36) ... (-311,-48)->(-318,-31)
R=4.0; nt=0; dmax=0
for o in gobs:
    Mw=o.matrix_world; Mi=Mw.inverted()
    for v in o.data.vertices:
        w=Mw@v.co
        if not (-396<w.x<-305 and -67<w.y<-15) or pip(w.x,w.y): continue
        d,i=edist_i(w.x,w.y)
        if d>=R or i not in FE: continue
        zt=fz(w.x,w.y)+0.04-0.08; t=(d/R)**1.5; zn=zt*(1-t)+w.z*t
        if w.z>zn: dmax=max(dmax,w.z-zn); w.z=zn; v.co=Mi@w; nt+=1
    o.data.update()
pv['ws268b']=1
print(TAG,'feather verts lowered',nt,'max drop',round(dmax,2),flush=True)
