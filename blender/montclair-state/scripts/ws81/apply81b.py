# ws81b: (1) Terrain faces under the unmodelled Sprague grandstand that still use the raw ortho (Ground_ortho_grass -> roof-stripe white lines)
# switched to the lawn material inside the ws80 lawn mask; (2) holes in the ground (see-through to Context_ground at z 0.5 = the thin dark
# line / black wedge) filled with a lawn patch on the WS78 DTM target.
import bpy,bmesh,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree


R='/workspace/nj-scenes/montclair-state/'
M=np.load(R+'scripts/ws81/ws80_mask.npy')
def mask(x,y):
    c=int((x+350)/0.5); r=int(220-(y+165)/0.5)
    return 0<=c<300 and 0<=r<220 and M[r,c]>127
T=bpy.data.objects['Terrain_LiDAR_DTM_1m']; me=T.data
names=[m.name if m else None for m in me.materials]
print('WS81b terrain mats',names,flush=True)
li=names.index('Lawn_Varied_Oct_local_fade'); oi=[i for i,n in enumerate(names) if n=='Ground_ortho_grass']
mw=T.matrix_world; ch=0
for p in me.polygons:
    if p.material_index in oi:
        c=mw@p.center
        if -270<c.x<-225 and -150<c.y<-90 and mask(c.x,c.y): p.material_index=li; ch+=1
me.update(); print('WS81b terrain faces -> lawn',ch,flush=True)
dg=bpy.context.evaluated_depsgraph_get()
def bvh(o):
    oe=o.evaluated_get(dg); m=oe.to_mesh(); b=bmesh.new(); b.from_mesh(m); b.transform(o.matrix_world); t=BVHTree.FromBMesh(b); b.free(); oe.to_mesh_clear(); return t
X0,X1,Y0,Y1=-272,-212,-142,-88
G=[]
for o in bpy.data.objects:
    if o.type!='MESH' or o.hide_render or o.name.startswith(('T_','Context_ground_beyond')): continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]; xs=[q.x for q in bb]; ys=[q.y for q in bb]
    if min(xs)<X1 and max(xs)>X0 and min(ys)<Y1 and max(ys)>Y0 and max(xs)-min(xs)<5000:
        G.append((o.name,bvh(o)))
print('WS81b ground objs',len(G),[n[:24] for n,_ in G][:40],flush=True)
TGT=bvh(bpy.data.objects['WS78_lot_pocket_DTM_target']); TG2=bvh(bpy.data.objects['WS68_RHD_ground_northDTM (north grid_1m dtm_filled; NJ 2020 ort'] if 'WS68_RHD_ground_northDTM (north grid_1m dtm_filled; NJ 2020 ort' in bpy.data.objects else T)
S=0.25; holes={}
nx=int((X1-X0)/S); ny=int((Y1-Y0)/S)
for i in range(nx):
    for j in range(ny):
        x=X0+(i+.5)*S; y=Y0+(j+.5)*S; hit=False
        for n,t in G:
            if t.ray_cast(Vector((x,y,400)),Vector((0,0,-1)))[0] is not None: hit=True; break
        if not hit:
            h=TGT.ray_cast(Vector((x,y,400)),Vector((0,0,-1)))[0]
            if h is None: h=TG2.ray_cast(Vector((x,y,400)),Vector((0,0,-1)))[0]
            if h is not None: holes[(i,j)]=h.z
print('WS81b hole cells',len(holes),flush=True)
if holes:
    xs=[X0+(i+.5)*S for i,j in holes]; ys=[Y0+(j+.5)*S for i,j in holes]
    print('WS81b hole bbox',round(min(xs),1),round(max(xs),1),round(min(ys),1),round(max(ys),1),flush=True)
    # dilate by 1 cell so the patch tucks under the hole rims
    cells=dict(holes)
    for (i,j),z in list(holes.items()):
        for di in (-1,0,1):
            for dj in (-1,0,1):
                k=(i+di,j+dj)
                if k not in cells:
                    h=TGT.ray_cast(Vector((X0+(k[0]+.5)*S,Y0+(k[1]+.5)*S,400)),Vector((0,0,-1)))[0]
                    if h is not None: cells[k]=h.z-0.03
    bm=bmesh.new(); vm={}
    def gv(i,j):
        if (i,j) not in vm:
            zs=[cells[k] for k in ((i,j),(i-1,j),(i,j-1),(i-1,j-1)) if k in cells]
            vm[(i,j)]=bm.verts.new((X0+i*S,Y0+j*S,min(zs)-0.01))
        return vm[(i,j)]
    for (i,j) in cells: bm.faces.new([gv(i,j),gv(i+1,j),gv(i+1,j+1),gv(i,j+1)])
    uv=bm.loops.layers.uv.new('UVMap')
    for f in bm.faces:
        for l in f.loops: l[uv].uv=(l.vert.co.x/4,l.vert.co.y/4)
    pm=bpy.data.meshes.new('WS81_ground_hole_patch'); bm.to_mesh(pm); bm.free()
    pm.materials.append(bpy.data.materials['Lawn_Varied_Oct_local_fade'])
    po=bpy.data.objects.new('WS81_ground_hole_patch_lawn_DTM',pm); T.users_collection[0].objects.link(po)
    print('WS81b patch faces',len(pm.polygons),flush=True)
bpy.ops.wm.save_mainfile(); print('WS81b SAVED',flush=True)
