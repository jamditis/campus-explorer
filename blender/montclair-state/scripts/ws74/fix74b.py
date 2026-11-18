# ws74b: cogen lot rebuilt as ONE continuous asphalt surface from the NJ 2020 ortho mask (scripts/ws74/mask.npy, 0.5 m cells),
# draped on the WS68 north-DTM ground +4 cm; cells under roads/walks/curbs/buildings/deck/tree trunks dropped; replaces the fn_lot_asphalt
# faces of gb_cogen_paving (retaining-wall faces kept) and hides fn_rhd_aisle_asphalt (kept in file, hide_render/hide_viewport).
import bpy,bmesh,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
D='/workspace/nj-scenes/montclair-state/scripts/ws74/'
M=np.load(D+'mask.npy'); X0,X1,Y0,Y1,S=np.load(D+'mask_grid.npy')
dg=bpy.context.evaluated_depsgraph_get()
def bvh(o):
    oe=o.evaluated_get(dg); m=oe.to_mesh(); bm=bmesh.new(); bm.from_mesh(m); bm.transform(o.matrix_world); t=BVHTree.FromBMesh(bm); bm.free(); oe.to_mesh_clear(); return t
G=[o for o in bpy.data.objects if o.name.startswith('WS68_RHD_ground')][0]; TG=bvh(G)
SKIPN=('WS68_RHD_ground','Terrain_LiDAR','Context_skirt','WS60_terrain','gb_cogen_paving','fn_rhd_aisle_asphalt','WS74_','WS70_gap','WS73_curb_back_clamp','helper')
blk=[]
for o in bpy.data.objects:
    if o.type!='MESH' or o.hide_render or any(o.name.startswith(k) or k in o.name for k in SKIPN): continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]; xs=[p.x for p in bb]; ys=[p.y for p in bb]
    if min(xs)<X1+1 and max(xs)>X0-1 and min(ys)<Y1+1 and max(ys)>Y0-1 and max(xs)-min(xs)<400:
        if len(o.data.vertices)>400000: continue
        blk.append((o.name,bvh(o)))
print('W74b blockers',len(blk),[n[:30] for n,_ in blk][:40],flush=True)
ny,nx=M.shape; keep=M.copy(); why={}
for j in range(ny):
    for i in range(nx):
        if not M[j,i]: continue
        x=X0+(i+0.5)*S; y=Y0+(j+0.5)*S
        g=TG.ray_cast(Vector((x,y,300)),Vector((0,0,-1)))[0]
        if not g: keep[j,i]=False; why['noground']=why.get('noground',0)+1; continue
        for n,t in blk:
            h=t.ray_cast(Vector((x,y,300)),Vector((0,0,-1)))[0]
            if h and h.z>g.z-0.5:
                keep[j,i]=False; why[n[:30]]=why.get(n[:30],0)+1; break
print('W74b cells mask',int(M.sum()),'kept',int(keep.sum()),'dropped by',sorted(why.items(),key=lambda a:-a[1])[:15],flush=True)
for _ in range(2):
    k=keep.astype(int); nb=np.zeros_like(k); nb[1:]+=k[:-1]; nb[:-1]+=k[1:]; nb[:,1:]+=k[:,:-1]; nb[:,:-1]+=k[:,1:]
    keep=keep&(nb>=2)
bm=bmesh.new(); vid={}
def V(i,j):
    k=(i,j)
    if k not in vid:
        x=X0+i*S; y=Y0+j*S; g=TG.ray_cast(Vector((x,y,300)),Vector((0,0,-1)))[0]
        vid[k]=bm.verts.new((x,y,(g.z if g else 0)+0.04))
    return vid[k]
for j in range(ny):
    for i in range(nx):
        if keep[j,i]: bm.faces.new((V(i,j),V(i+1,j),V(i+1,j+1),V(i,j+1)))
uv=bm.loops.layers.uv.new('UVMap')
for f in bm.faces:
    for l in f.loops: l[uv].uv=(l.vert.co.x/4,l.vert.co.y/4)
pts=[v.co.copy() for v in bm.verts]
me=bpy.data.meshes.new('WS74_cogen_lot_asphalt_ortho2020'); bm.to_mesh(me); bm.free()
me.materials.append(bpy.data.materials['fn_lot_asphalt'])
ob=bpy.data.objects.new('WS74_cogen_lot_asphalt_ortho2020_UNVERIFIED_edges',me)
gp=bpy.data.objects['gb_cogen_paving']; (gp.users_collection[0] if gp.users_collection else bpy.context.scene.collection).objects.link(ob)
print('W74b lot faces',len(me.polygons),flush=True)
# remove asphalt faces from gb_cogen_paving, keep retaining concrete
mi=[k for k,s in enumerate(gp.material_slots) if s.material and s.material.name=='fn_lot_asphalt']
bm=bmesh.new(); bm.from_mesh(gp.data); df=[f for f in bm.faces if f.material_index in mi]; n0=len(df)
bmesh.ops.delete(bm,geom=df,context='FACES'); bm.to_mesh(gp.data); bm.free(); gp.data.update(); print('W74b gb_cogen_paving asphalt faces removed',n0,flush=True)
a=bpy.data.objects['fn_rhd_aisle_asphalt']; a.hide_render=True; a.hide_viewport=True; a['ws74_hidden']=1
# lot ground must not poke through: count ground hits above the lot
T=bvh(ob); hi=0; nn=0
for c in pts[::7]:
    g=TG.ray_cast(Vector((c.x+0.13,c.y+0.11,300)),Vector((0,0,-1)))[0]; h=T.ray_cast(Vector((c.x+0.13,c.y+0.11,300)),Vector((0,0,-1)))[0]
    if g and h: nn+=1; hi+= g.z>h.z-0.005
print('W74b ground above lot',hi,'/',nn,flush=True)
