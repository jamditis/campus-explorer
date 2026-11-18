# ws75b: the "dark bars" S of the cogen lot (x -255..-222, y -135..-90) were visible Roads_OSM ribbon faces (OSM parking aisles; ws74's probe
# skipped big-span objects). The 2020 ortho shows a real asphalt lot there (N of / E of Sprague Field's east grandstand).
# Build WS75_sprague_lot_asphalt_ortho2020 (0.4 m cells from scripts/ws75/mask2.npy, draped +4 cm on max(WS68 ground, Terrain DTM)),
# drop cells under other meshes, then delete only the Roads_OSM faces that were VISIBLE (top-most) in that box (scripts/ws75/roads_sel.json).
import bpy,bmesh,numpy as np,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
D='/workspace/nj-scenes/montclair-state/scripts/ws75/'
M=np.load(D+'mask2.npy'); X0,X1,Y0,Y1,S=np.load(D+'mask2_grid.npy')
dg=bpy.context.evaluated_depsgraph_get()
def bvh(o):
    oe=o.evaluated_get(dg); m=oe.to_mesh(); bm=bmesh.new(); bm.from_mesh(m); bm.transform(o.matrix_world); t=BVHTree.FromBMesh(bm); bm.free(); oe.to_mesh_clear(); return t
grounds=[o for o in bpy.data.objects if o.name.startswith('WS68_RHD_ground') or o.name=='Terrain_LiDAR_DTM_1m']
TG=[bvh(o) for o in grounds]
def gz(x,y):
    zs=[h[0].z for h in (t.ray_cast(Vector((x,y,300)),Vector((0,0,-1))) for t in TG) if h[0]]
    return max(zs) if zs else None
SKIPN=('WS68_RHD_ground','Terrain_LiDAR','Context_skirt','WS60_terrain','Roads_OSM','WS75_','WS70_gap','WS73_curb_back_clamp','helper','OZ_walk_joints','_DTM_target','QG_','QI_','QJ_','WF_')
blk=[]
for o in bpy.data.objects:
    if o.type!='MESH' or o.hide_render or any(o.name.startswith(k) or k in o.name for k in SKIPN): continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]; xs=[p.x for p in bb]; ys=[p.y for p in bb]
    if min(xs)<X1 and max(xs)>X0 and min(ys)<Y1 and max(ys)>Y0 and len(o.data.vertices)<400000:
        # only objects that actually overlap the mask box
        jx0=max(0,int((min(xs)-X0)/S)); jx1=int((max(xs)-X0)/S)+1; jy0=max(0,int((min(ys)-Y0)/S)); jy1=int((max(ys)-Y0)/S)+1
        if M[jy0:jy1,jx0:jx1].any(): blk.append((o.name,bvh(o)))
print('WS75b blockers',len(blk),[n[:28] for n,_ in blk][:30],flush=True)
ny,nx=M.shape; keep=M.copy(); why={}
for j in range(ny):
    for i in range(nx):
        if not M[j,i]: continue
        x=X0+(i+0.5)*S; y=Y0+(j+0.5)*S; g=gz(x,y)
        if g is None: keep[j,i]=False; continue
        for n,t in blk:
            h=t.ray_cast(Vector((x,y,300)),Vector((0,0,-1)))[0]
            if h and h.z>g-0.5: keep[j,i]=False; why[n[:28]]=why.get(n[:28],0)+1; break
for _ in range(2):
    k=keep.astype(int); nb=np.zeros_like(k); nb[1:]+=k[:-1]; nb[:-1]+=k[1:]; nb[:,1:]+=k[:,:-1]; nb[:,:-1]+=k[:,1:]; keep=keep&(nb>=2)
print('WS75b cells',int(M.sum()),'kept',int(keep.sum()),'dropped',sorted(why.items(),key=lambda a:-a[1])[:10],flush=True)
bm=bmesh.new(); vid={}
def V(i,j):
    if (i,j) not in vid:
        x=X0+i*S; y=Y0+j*S; g=gz(x,y); vid[(i,j)]=bm.verts.new((x,y,(g if g is not None else 120)+0.04))
    return vid[(i,j)]
for j in range(ny):
    for i in range(nx):
        if keep[j,i]: bm.faces.new((V(i,j),V(i+1,j),V(i+1,j+1),V(i,j+1)))
# soften stair steps: smooth boundary verts in XY a little (2 passes), re-drape
bnd=[v for v in bm.verts if v.is_boundary]
for _ in range(2):
    new={}
    for v in bnd:
        nbv=[e.other_vert(v) for e in v.link_edges if e.is_boundary]
        if len(nbv)==2: new[v]=(v.co.xy*0.5+(nbv[0].co.xy+nbv[1].co.xy)*0.25)
    for v,c in new.items(): v.co.x,v.co.y=c.x,c.y
for v in bnd:
    g=gz(v.co.x,v.co.y)
    if g is not None: v.co.z=g+0.04
uv=bm.loops.layers.uv.new('UVMap')
for f in bm.faces:
    for l in f.loops: l[uv].uv=(l.vert.co.x/4,l.vert.co.y/4)
me=bpy.data.meshes.new('WS75_sprague_lot_asphalt_ortho2020'); bm.to_mesh(me); bm.free()
me.materials.append(bpy.data.materials['fn_lot_asphalt'])
ob=bpy.data.objects.new('WS75_sprague_lot_asphalt_ortho2020_UNVERIFIED_edges',me)
ref=bpy.data.objects.get('WS74_cogen_lot_asphalt_ortho2020_UNVERIFIED_edges')
(ref.users_collection[0] if ref and ref.users_collection else bpy.context.scene.collection).objects.link(ob)
print('WS75b lot faces',len(me.polygons),flush=True)
# delete visible Roads_OSM faces in the box
sel=json.load(open(D+'roads_sel.json')); kill=set(i for i,k,top,x,y in sel if top=='Roads_OSM' and -262<=x<=-217 and -135<=y<=-80)
ro=bpy.data.objects['Roads_OSM']; bm=bmesh.new(); bm.from_mesh(ro.data); bm.faces.ensure_lookup_table()
df=[bm.faces[i] for i in kill if i<len(bm.faces)]; bmesh.ops.delete(bm,geom=df,context='FACES'); bm.to_mesh(ro.data); bm.free(); ro.data.update()
print('WS75b Roads_OSM faces deleted',len(df),flush=True)
