# ws151 UNIFY #56: (a) retire the OSM kerb Curbs_granite_OSM spline 0 points 0..31 (x -67.6 Skyline W edge y -210.8..-171,
# then W along y -170 to x -68.8): 2023 LiDAR class-2 intensity 2.1-3.3k both sides (asphalt) and only the smooth 4 % road
# cross-fall across it (no 0.10-0.15 m step) -> no curb there; keep from pt 32 (x -70.3) where concrete 6-9k + 0.10-0.14 m step begin.
# (b) one unified apron surface Lot 9 E edge -> Skyline Way (replaces the WS148 / WS150c patches whose height steps read as seams).
import bpy, bmesh, json, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
M='/workspace/nj-scenes/montclair-state/'
cu=bpy.data.objects['Curbs_granite_OSM'].data
s0=cu.splines[0]
mwc=bpy.data.objects['Curbs_granite_OSM'].matrix_world
p0=mwc@s0.points[0].co.to_3d(); print("FIX151_S0_FIRST",tuple(round(c,2) for c in p0))
if abs(p0.x+67.6)<0.3 and abs(p0.y+210.84)<0.3:
    keep=[(p.co.copy(),p.radius,p.tilt,p.weight) for p in list(s0.points)[32:]]
    ns=cu.splines.new('POLY'); ns.points.add(len(keep)-1)
    for p,(co,r,t,w) in zip(ns.points,keep): p.co=co; p.radius=r; p.tilt=t; p.weight=w
    ns.use_cyclic_u=s0.use_cyclic_u; ns.material_index=s0.material_index
    cu.splines.remove(s0); print("FIX151_CURB_TRIM kept",len(keep),"first",tuple(round(c,2) for c in (mwc@ns.points[0].co.to_3d())))
else: print("FIX151_CURB_SKIP spline0 not found")
# --- (b) unified apron
D=np.load(M+'scripts/ws142/dtm142.npy'); X0,Y1,R=-95.0,-162.0,0.5
def dz(x,y):
    fx=(x-X0)/R; fy=(Y1-y)/R; j=int(fx); i=int(fy); tx=fx-j; ty=fy-i; Z=D[1]
    return (Z[i,j]*(1-tx)+Z[i,j+1]*tx)*(1-ty)+(Z[i+1,j]*(1-tx)+Z[i+1,j+1]*tx)*ty
sp2=json.load(open(M+'scripts/ws151/curbs_osm.json'))['2']
c2=sorted([(p[1],p[0]) for p in sp2 if -215<p[1]<-170 and p[0]<-58])
def xe(y): return float(np.interp(y,[a for a,b in c2],[b for a,b in c2]))-0.05
XW,YS,YN=-69.6,-191.5,-178.7
OLD=[o for o in bpy.data.objects if o.name.startswith(('WS148_Lot9_E_apron','WS150_Lot9_E_apron_Skyline_N_end_strip'))]
for o in OLD: o.hide_render=True; o.hide_viewport=True; o.name=o.name[:40]+'_RETIRED_ws151'
under=[o for o in bpy.data.objects if o.type=='MESH' and not o.hide_render and (o.name=='Roads_OSM' or o.name.startswith(('WS142_Lot9_asphalt','WS135a_Skyline_Way_asphalt','WS150_Lot9_E_apron_S','WS145_walk_nose_lot_asphalt')))]
dg=bpy.context.evaluated_depsgraph_get(); b=bmesh.new()
for o in under:
    oe=o.evaluated_get(dg); me=oe.to_mesh(); mw=o.matrix_world
    t=bmesh.new(); t.from_mesh(me); t.transform(mw)
    dead=[f for f in t.faces if not all(XW-2<v.co.x<-60 and YS-2<v.co.y<YN+2 for v in f.verts)]
    bmesh.ops.delete(t,geom=dead,context='FACES'); m2=bpy.data.meshes.new('tmp151'); t.to_mesh(m2); t.free(); b.from_mesh(m2); bpy.data.meshes.remove(m2); oe.to_mesh_clear()
    print("FIX151_UNDER",o.name[:40])
T=BVHTree.FromBMesh(b); b.free()
def top(x,y):
    h=T.ray_cast(Vector((x,y,140.0)),Vector((0,0,-1))); return h[0].z if h[0] is not None else None
# offset of paving over LiDAR (median over box)
offs=[top(x,y)-dz(x,y) for x in np.arange(XW+0.3,-63,0.7) for y in np.arange(YS+0.3,YN,0.7) if top(x,y) is not None]
OFF=float(np.median(offs)); print("FIX151_OFF",round(OFF,3),len(offs))
G=0.25; me=bpy.data.meshes.new('WS151_Lot9_E_apron_unified_to_Skyline_LiDAR2023_UNIFY56'); bm=bmesh.new(); V={}
xs=np.arange(XW,-61.0,G); ys=np.arange(YS,YN+1e-6,G)
def inside(x,y): return XW-1e-6<=x<=xe(y)+1e-6
def gv(i,k):
    if (i,k) not in V:
        x=min(xs[i],xe(ys[k])) ; y=ys[k]
        V[(i,k)]=bm.verts.new((x,y,0.0))
    return V[(i,k)]
for i in range(len(xs)-1):
    for k in range(len(ys)-1):
        if xs[i]<xe(ys[k])-0.02 and xs[i]<xe(ys[k+1])-0.02:
            q=[gv(i,k),gv(i+1,k),gv(i+1,k+1),gv(i,k+1)]
            if len({v.co.to_tuple() for v in q})==4: bm.faces.new(q)
bm.verts.ensure_lookup_table()
for v in bm.verts:
    x,y=v.co.x,v.co.y; tgt=dz(x,y)+OFF; ex=top(x,y)
    d=min(x-XW, xe(y)-x, y-YS, YN-y); w=max(0.0,min(1.0,d/1.0))
    base=ex if ex is not None else tgt
    z=(1-w)*base+w*tgt
    if ex is not None: z=max(z,ex+0.004)
    v.co.z=z
for it in range(4):   # gentle smoothing of interior, keep clearance
    nz={}
    for v in bm.verts:
        if v.is_boundary: continue
        nb=[e.other_vert(v).co.z for e in v.link_edges]; nz[v]=0.5*v.co.z+0.5*sum(nb)/len(nb)
    for v,z in nz.items():
        ex=top(v.co.x,v.co.y); v.co.z=max(z,ex+0.004) if ex is not None else z
ed=[e for e in bm.edges if e.is_boundary]; r=bmesh.ops.extrude_edge_only(bm,edges=ed)
for v in [g for g in r['geom'] if isinstance(g,bmesh.types.BMVert)]: v.co.z-=0.08
bm.to_mesh(me); bm.free(); ob=bpy.data.objects.new(me.name,me)
ref=[o for o in bpy.data.objects if o.name.startswith('WS142_Lot9_asphalt')][0]
for c in ref.users_collection: c.objects.link(ob)
me.materials.append(bpy.data.materials['Asphalt'])
print("FIX151_APRON faces",len(me.polygons),"x",XW,"..xe y",YS,YN)
tr=bpy.data.objects['Terrain_LiDAR_DTM_1m']; tm=tr.matrix_world; tmi=tm.inverted(); n=0
TB=BVHTree.FromObject(ob,dg) if False else None
for v in tr.data.vertices:
    w_=tm@v.co
    if XW-0.2<w_.x<-61.5 and YS-0.2<w_.y<YN+0.2:
        lim=dz(w_.x,w_.y)+OFF-0.08
        if w_.z>lim: w_.z=lim; v.co=tmi@w_; n+=1
tr.data.update(); print("FIX151_TERRAIN_LOWERED",n)
