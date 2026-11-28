# ws268 (merge208 CHAIN, on main ws267c): UNIFY W72 — College Avenue + Lot 33 south of the police building.
# Evidence: OSM College Avenue way 232850521 (centreline (-328,-37)->(-392,-21)), Lot 33 amenity=parking way 312848723,
# Carlisle Road 583841726 (W end); NJ 2020 ortho: one continuous paved area from the police lawn / walk (N curb ~y -21.5 at x -350,
# ~-20 at x -378) south through Lot 33. The model had no road or lot here: the ortho was draped on lumpy dtm_filled terrain
# (WS68 / M3b) with a hole (~x -357..-350, y -30..-50) where only the low 4 km skirt showed (dark notch).
# Build: one paved surface (1 m grid, polygon from OSM + ortho), z = robust quadratic fit of the base ground + 4 cm (removes lumps,
# keeps the ~5% eastward rise), 0.6 m skirt down at the edges, faces under the police walk / terrace walls / deck / Maintenance
# Building removed; terrain base verts inside the polygon (0.5 m inset) pushed 12 cm under the paving. Material = Roads_OSM's.
# Lane/stall markings, tree islands and curbs not modelled (UNVERIFIED). N curb line from the ortho (OSM centre ~2 m off).
import bpy, bmesh, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
TAG='F268A'
if bpy.data.objects.get('WS268_W72_CollegeAve_Lot33_paving_UNVERIFIED'): raise SystemExit('F268A already applied')
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
fz=lambda x,y: float(basis(np.array(x),np.array(y))@c)
# grid mesh 1 m, clipped to polygon by vertex test (quads with all 4 corners inside or clipped tris), plus boundary ring
bm=bmesh.new(); V={}
def vert(x,y):
    k=(round(x,3),round(y,3))
    if k not in V: V[k]=bm.verts.new((x,y,fz(x,y)+0.04))
    return V[k]
G=np.arange(-391,-309,1.0); H=np.arange(-62,-18,1.0); inside=lambda x,y: poly.contains_point((x,y))
nf=0; nb=0
for x in G:
    for y in H:
        q=[(x,y),(x+1,y),(x+1,y+1),(x,y+1)]
        if not all(inside(*p) for p in q): continue
        cx,cy=x+0.5,y+0.5
        if blocked(cx,cy,fz(cx,cy)): nb+=1; continue
        bm.faces.new([vert(*p) for p in q]); nf+=1
print(TAG,'grid faces',nf,'blocked',nb,flush=True)
# boundary fill: thin strip between the grid's outer edge and the true polygon, done by extruding boundary edges outward is complex;
# instead add a polygon-edge ribbon: triangles fan from boundary samples (0.5 m step) to nearest grid vertex.
bm.verts.ensure_lookup_table()
GL=list(bm.verts); gv=np.array([v.co.xy[:] for v in GL]); nr=0
Pc=P+[P[0]]
for (x0,y0),(x1,y1) in zip(Pc[:-1],Pc[1:]):
    L=((x1-x0)**2+(y1-y0)**2)**.5; n=max(1,int(L/0.7))
    pts=[(x0+(x1-x0)*i/n,y0+(y1-y0)*i/n) for i in range(n+1)]
    for (ax,ay),(bx,by) in zip(pts[:-1],pts[1:]):
        mx,my=(ax+bx)/2,(ay+by)/2
        if blocked(mx,my,fz(mx,my)): continue
        d=((gv[:,0]-mx)**2+(gv[:,1]-my)**2); i=int(d.argmin())
        if d[i]>2.5**2: continue
        a=vert(ax,ay); b=vert(bx,by); g=GL[i]
        try: bm.faces.new([a,b,g]); nr+=1
        except ValueError: pass
print(TAG,'ribbon tris',nr,flush=True)
# skirt: boundary edges extruded down 0.6 m
bm.edges.ensure_lookup_table()
be=[e for e in bm.edges if e.is_boundary]
r=bmesh.ops.extrude_edge_only(bm,edges=be)
for v in [g for g in r['geom'] if isinstance(g,bmesh.types.BMVert)]: v.co.z-=0.6
bmesh.ops.recalc_face_normals(bm,faces=bm.faces[:])
for f in bm.faces:
    if f.normal.z<-0.5: f.normal_flip()
me=bpy.data.meshes.new('WS268_W72_CollegeAve_Lot33_paving'); bm.to_mesh(me); bm.free()
ob=bpy.data.objects.new('WS268_W72_CollegeAve_Lot33_paving_UNVERIFIED',me)
rd=bpy.data.objects.get('Roads_OSM'); mat=rd.material_slots[0].material if rd and rd.material_slots else None
if mat: me.materials.append(mat)
print(TAG,'material',mat and mat.name,flush=True)
col=(rd.users_collection[0] if rd else bpy.context.scene.collection); col.objects.link(ob)
# push terrain base verts under the paving (0.5 m inset)
nt=0
for o in gobs:
    Mw=o.matrix_world; Mi=Mw.inverted()
    for v in o.data.vertices:
        w=Mw@v.co
        if -392<w.x<-309 and -63<w.y<-18 and pip(w.x,w.y) and edist(w.x,w.y)>=0.5:
            zt=fz(w.x,w.y)+0.04-0.12
            if w.z>zt: w.z=zt; v.co=Mi@w; nt+=1
    o.data.update()
print(TAG,'terrain verts lowered',nt,flush=True)
ob['ws268']='W72 College Ave + Lot 33 paving (OSM 232850521, 312848723; NJ 2020 ortho); markings/islands/curbs UNVERIFIED'
print(TAG,'done verts',len(me.vertices),'faces',len(me.polygons),flush=True)
