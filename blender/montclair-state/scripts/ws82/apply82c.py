# ws82a: (1) Sprague east lane rebuilt as ONE 0.2 m grid surface on the TOP z of WS75/WS80 (outline snapped to the ws80 polygon),
#        WS75/WS80 cells in the lane deleted -> no step-shadow cracks.  (2) grandstand-lawn Terrain faces -> WS82 lawn copy with the ortho
#        colour source forced to the flat lawn override (kills the white ortho streaks).
import bpy,bmesh,math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
P=[(-264,-86),(-264,-95.5),(-230.3,-108.3),(-230.3,-127),(-229,-130.5),(-224,-131),(-221.5,-128),(-220.3,-120),(-219.8,-110),(-217.5,-108),(-216.5,-96),(-216.5,-86)]
def inside(x,y):
    c=False; n=len(P)
    for i in range(n):
        x1,y1=P[i]; x2,y2=P[(i+1)%n]
        if (y1>y)!=(y2>y) and x<(x2-x1)*(y-y1)/(y2-y1)+x1: c=not c
    return c
def nearest_on_poly(x,y):
    best=None
    for i in range(len(P)):
        x1,y1=P[i]; x2,y2=P[(i+1)%len(P)]; dx,dy=x2-x1,y2-y1; L=dx*dx+dy*dy
        t=max(0,min(1,((x-x1)*dx+(y-y1)*dy)/L)); qx,qy=x1+t*dx,y1+t*dy; d=(qx-x)**2+(qy-y)**2
        if best is None or d<best[0]: best=(d,qx,qy)
    return best[1],best[2]
XL,YN=-231.0,-106.0
def inlane(x,y): return x>XL and y<YN and inside(x,y)
dg=bpy.context.evaluated_depsgraph_get()
def bvh_me(m):
    b=bmesh.new(); b.from_mesh(m); t=BVHTree.FromBMesh(b); b.free(); return t
def bvh(o):
    b=bmesh.new(); b.from_mesh(o.data); b.transform(o.matrix_world); t=BVHTree.FromBMesh(b); b.free(); return t
L75=bpy.data.objects['WS75_sprague_lot_asphalt_ortho2020_UNVERIFIED_edges']; L80=bpy.data.objects['WS80_sprague_lot_fill_asphalt_ortho2020_UNVERIFIED_edges']
BK='/workspace/nj-scenes/montclair-state/montclair_state_pre_20261112ws82.blend'
with bpy.data.libraries.load(BK,link=True) as (src,dst): dst.meshes=[L75.data.name,L80.data.name]
TB=[bvh_me(m) for m in dst.meshes]
for lib in list(bpy.data.libraries):
    if lib.filepath==BK: bpy.data.libraries.remove(lib)
FP=bpy.data.objects.get('Footpaths_OSM'); FB=bvh(FP)
def under_walk(x,y): return FB.ray_cast(Vector((x,y,300)),Vector((0,0,-1)))[0] is not None
def topz(x,y):
    zs=[h[0].z for h in (t.ray_cast(Vector((x,y,300)),Vector((0,0,-1))) for t in TB) if h[0]]
    return max(zs) if zs else None
def topz_near(x,y):
    z=topz(x,y)
    if z is not None: return z
    for r in (0.1,0.2,0.3,0.45):
        zs=[topz(x+r*math.cos(a),y+r*math.sin(a)) for a in [k*math.pi/4 for k in range(8)]]
        zs=[q for q in zs if q is not None]
        if zs: return max(zs)
    return None
S=0.2; X0,X1,Y0,Y1=-231.0,-219.0,-131.6,-105.8
nx=int(round((X1-X0)/S)); ny=int(round((Y1-Y0)/S))
def gp(i,j): return X0+i*S, Y0+j*S
use=set()
for i in range(nx):
    for j in range(ny):
        cs=[gp(i,j),gp(i+1,j),gp(i+1,j+1),gp(i,j+1)]
        if any(x>XL-1e-6 and y<YN+0.21 and inside(x,y) for x,y in cs): use.add((i,j))
bm=bmesh.new(); vm={}; miss=0; unk=set(); MX=[]
POS={}
def info(i,j):
    if (i,j) in POS: return POS[(i,j)]
    x,y=gp(i,j)
    if not inside(x,y): x,y=nearest_on_poly(x,y)
    z=topz(x,y)
    if z is None and inside(*gp(i,j)): z=topz(*gp(i,j))
    if z is None and not inside(*gp(i,j)): z=topz_near(x,y) if topz_near(*gp(i,j)) is not None and abs(x-gp(i,j)[0])+abs(y-gp(i,j)[1])<0.15 else None
    POS[(i,j)]=(x,y,z); return POS[(i,j)]
def V(i,j):
    global miss
    if (i,j) in vm: return vm[(i,j)]
    x,y,z=info(i,j)
    v=bm.verts.new((x,y,(z if z is not None else 0.0)+0.003)); vm[(i,j)]=v
    if z is None: miss+=1; unk.add(v); MX.append((x,y))
    return v
for (i,j) in sorted(use):
    ks=[(i,j),(i+1,j),(i+1,j+1),(i,j+1)]
    kn=[info(*k)[2] is not None for k in ks]
    if sum(kn)<2 and not (sum(kn)>=1 and all(kn[q] or under_walk(*info(*ks[q])[:2]) for q in range(4))): continue
    vs=[V(*k) for k in ks]
    if len(set(vs))==4:
        try: bm.faces.new(vs)
        except ValueError: pass
bm.verts.ensure_lookup_table()
for it in range(200):
    if not unk: break
    done=[]
    for v in unk:
        nb=[e.other_vert(v) for e in v.link_edges if e.other_vert(v) not in unk]
        if nb: v.co.z=sum(q.co.z for q in nb)/len(nb); done.append(v)
    for v in done: unk.discard(v)
open('/workspace/nj-scenes/montclair-state/scripts/ws82/miss.txt','w').write('\n'.join('%.2f %.2f'%q for q in MX))
print('WS82c unresolved',len(unk),flush=True)
UNKXY=[(round(v.co.x,1),round(v.co.y,1)) for v in list(unk)[:5]]
FP=bpy.data.objects.get('Footpaths_OSM'); tuck=0
if FP:
    FB=bvh(FP)
    for v in bm.verts:
        h=FB.ray_cast(Vector((v.co.x,v.co.y,300)),Vector((0,0,-1)))[0]
        if h and abs(h.z-v.co.z)<0.6 and h.z<v.co.z+0.01: v.co.z=h.z-0.015; tuck+=1
print('WS82c tucked under Footpaths',tuck,flush=True)
bmesh.ops.remove_doubles(bm,verts=bm.verts,dist=0.01)
deg=[f for f in bm.faces if f.calc_area()<1e-4]; bmesh.ops.delete(bm,geom=deg,context='FACES')
uv=bm.loops.layers.uv.new('UVMap')
for f in bm.faces:
    for l in f.loops: l[uv].uv=(l.vert.co.x*0.25,l.vert.co.y*0.25)
for f in bm.faces: f.smooth=False
me=bpy.data.meshes.new('WS82_sprague_lane_onesurface'); bm.to_mesh(me); bm.free()
old=bpy.data.objects.get('WS82_sprague_lane_onesurface_asphalt_ortho2020_UNVERIFIED_edges')
if old: bpy.data.objects.remove(old)
ob=bpy.data.objects.new('WS82_sprague_lane_onesurface_asphalt_ortho2020_UNVERIFIED_edges',me); me.materials.append(bpy.data.materials['fn_lot_asphalt'])
for c in L75.users_collection: c.objects.link(ob)
print('WS82c lane faces',len(me.polygons),'verts',len(me.vertices),'miss',miss,'zrange',min(v.co.z for v in me.vertices),max(v.co.z for v in me.vertices),flush=True)
for L in (L75,L80):
    b=bmesh.new(); b.from_mesh(L.data); mw=L.matrix_world
    kill=[f for f in b.faces if (lambda c: inlane(c.x,c.y))(mw@f.calc_center_median())]
    n0=len(b.faces); bmesh.ops.delete(b,geom=kill,context='FACES'); lone=[v for v in b.verts if not v.link_faces]; bmesh.ops.delete(b,geom=lone,context='VERTS')
    b.to_mesh(L.data); b.free(); L.data.update(); print('WS82c deleted',L.name[:20],len(kill),'of',n0,flush=True)
# (2) grandstand lawn material
src=bpy.data.materials['Lawn_Varied_Oct_local_fade']
m=bpy.data.materials.get('WS82_Lawn_grandstand_no_ortho_UNVERIFIED')
if not m:
    m=src.copy(); m.name='WS82_Lawn_grandstand_no_ortho_UNVERIFIED'
    nt=m.node_tree; mix=nt.nodes['WS75_lawn_mix']
    for l in list(nt.links):
        if l.to_node==mix and l.to_socket.name=='Factor': nt.links.remove(l)
    mix.inputs['Factor'].default_value=1.0
    print('WS82c lawn B colour',[tuple(round(c,3) for c in s.default_value) for s in mix.inputs if s.name=='B' and hasattr(s,'default_value') and hasattr(s.default_value,'__len__')],flush=True)
T=bpy.data.objects['Terrain_LiDAR_DTM_1m']; me=T.data
if m.name not in [x.name for x in me.materials if x]: me.materials.append(m)
mi=[x.name if x else None for x in me.materials].index(m.name)
names=[x.name if x else None for x in me.materials]; okset={names.index(n) for n in ('Ground_ortho_grass','Lawn_Varied_Oct_local_fade','COLE_lawn_post2020_bs') if n in names}
mw=T.matrix_world; cnt={}
for p in me.polygons:
    c=mw@p.center
    if -256<=c.x<=-224 and -146<=c.y<=-104 and p.material_index in okset and not inside(c.x,c.y):
        cnt[names[p.material_index]]=cnt.get(names[p.material_index],0)+1; p.material_index=mi
print('WS82c lawn faces',cnt,flush=True)
cur=bpy.data.objects.get('WS81_terrain_W_edge_curtain_lawn_UNVERIFIED_grade')
if cur: cur.data.materials[0]=m
bpy.ops.wm.save_mainfile(); print('WS82c SAVED',flush=True)
# concrete slivers under/at the lane W edge (inside the lot polygon too)
T=bpy.data.objects['Terrain_LiDAR_DTM_1m']; me=T.data; names=[x.name if x else None for x in me.materials]
mi2=names.index('WS82_Lawn_grandstand_no_ortho_UNVERIFIED'); ci=names.index('WS3_Concrete_panels_sawcut'); n=0
for p in me.polygons:
    if p.material_index!=ci: continue
    c=T.matrix_world@p.center
    if -233<=c.x<=-226 and -132<=c.y<=-106: p.material_index=mi2; n+=1
print('WS82c concrete->lawn at lane W edge',n,flush=True)
bpy.ops.wm.save_mainfile(); print('WS82c SAVED2',flush=True)
