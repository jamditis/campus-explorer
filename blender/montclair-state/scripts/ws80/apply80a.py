# ws80a: Sprague lot S/W outline to the 2020 ortho (hand trace on scripts/ws77/ortho_sprague_grid.png).
# (1) clip WS75 lot cells outside the traced lot polygon (y<-90 only); (2) fill bare-ground gaps inside it (WS80 fill, BVH method as ws75b);
# (3) extend the WS75 lawn override east to x -230.3 south of the roof NE edge (data/ws80_sprague_lawn_mask.png).
import bpy,bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R='/workspace/nj-scenes/montclair-state/'
P=[(-264,-86),(-264,-95.5),(-230.3,-108.3),(-230.3,-127),(-229,-130.5),(-224,-131),(-221.5,-128),(-220.3,-120),(-219.8,-110),(-217.5,-108),(-216.5,-96),(-216.5,-86)]
def inside(x,y):
    c=False; n=len(P)
    for i in range(n):
        x1,y1=P[i]; x2,y2=P[(i+1)%n]
        if (y1>y)!=(y2>y) and x<(x2-x1)*(y-y1)/(y2-y1)+x1: c=not c
    return c
ob=bpy.data.objects['WS75_sprague_lot_asphalt_ortho2020_UNVERIFIED_edges']; mw=ob.matrix_world
bm=bmesh.new(); bm.from_mesh(ob.data); kill=[]
for f in bm.faces:
    c=mw@f.calc_center_median()
    if c.y<-90 and not inside(c.x,c.y): kill.append(f)
n0=len(bm.faces); bmesh.ops.delete(bm,geom=kill,context='FACES')
lone=[v for v in bm.verts if not v.link_faces]; bmesh.ops.delete(bm,geom=lone,context='VERTS')
bm.to_mesh(ob.data); bm.free(); ob.data.update()
print('WS80a clipped',len(kill),'of',n0,flush=True)
dg=bpy.context.evaluated_depsgraph_get()
def bvh(o):
    oe=o.evaluated_get(dg); m=oe.to_mesh(); b=bmesh.new(); b.from_mesh(m); b.transform(o.matrix_world); t=BVHTree.FromBMesh(b); b.free(); oe.to_mesh_clear(); return t
TG=[bvh(o) for o in bpy.data.objects if o.name.startswith('WS68_RHD_ground') or o.name=='Terrain_LiDAR_DTM_1m']
def gz(x,y):
    zs=[h[0].z for h in (t.ray_cast(Vector((x,y,300)),Vector((0,0,-1))) for t in TG) if h[0]]
    return max(zs) if zs else None
SKIPN=('WS68_RHD_ground','Terrain_LiDAR','Context_skirt','WS60_terrain','WS70_gap','WS73_curb_back_clamp','helper','OZ_walk_joints','_DTM_target','QG_','QI_','QJ_','WF_','T_','WS76_lot_')
X0,X1,Y0,Y1=-264.0,-216.4,-131.2,-88.0
blk=[]
for o in bpy.data.objects:
    if o.type!='MESH' or o.hide_render or any(o.name.startswith(k) or k in o.name for k in SKIPN): continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]; xs=[q.x for q in bb]; ys=[q.y for q in bb]
    if min(xs)<X1 and max(xs)>X0 and min(ys)<Y1 and max(ys)>Y0 and len(o.data.vertices)<400000: blk.append((o.name,bvh(o)))
print('WS80a blockers',len(blk),[n[:26] for n,_ in blk][:40],flush=True)
S=0.4; cells=[]; dbg={}
x=X0
while x<X1:
    y=Y0
    while y<Y1:
        cx,cy=x+S/2,y+S/2
        if inside(cx,cy):
            g=gz(cx,cy)
            if g is None: dbg['noground']=dbg.get('noground',0)+1
            else:
                hit=None
                for n,t in blk:
                    h=t.ray_cast(Vector((cx,cy,300)),Vector((0,0,-1)))[0]
                    if h and h.z>g-0.5: hit=n[:24]; break
                if hit: dbg[hit]=dbg.get(hit,0)+1
                else: cells.append((cx,cy,g))
        y+=S
    x+=S
print('WS80a fill cells',len(cells),sorted(dbg.items(),key=lambda a:-a[1])[:12],flush=True)
old=bpy.data.objects.get('WS80_sprague_lot_fill_asphalt_ortho2020_UNVERIFIED_edges')
if old: m=old.data; bpy.data.objects.remove(old); bpy.data.meshes.remove(m)
if cells:
    bm=bmesh.new(); vm={}
    def gv(ix,iy,z):
        k=(round(ix,2),round(iy,2))
        if k not in vm: vm[k]=[bm.verts.new((k[0],k[1],z)),1]
        else:
            v=vm[k]; v[0].co.z=(v[0].co.z*v[1]+z)/(v[1]+1); v[1]+=1
        return vm[k][0]
    for cx,cy,z in cells:
        zz=z+0.04
        bm.faces.new([gv(cx-S/2,cy-S/2,zz),gv(cx+S/2,cy-S/2,zz),gv(cx+S/2,cy+S/2,zz),gv(cx-S/2,cy+S/2,zz)])
    uv=bm.loops.layers.uv.new('UVMap')
    for f in bm.faces:
        for l in f.loops: l[uv].uv=(l.vert.co.x/4,l.vert.co.y/4)
    me=bpy.data.meshes.new('WS80_sprague_lot_fill'); bm.to_mesh(me); bm.free()
    me.materials.append(bpy.data.materials['fn_lot_asphalt'])
    fo=bpy.data.objects.new('WS80_sprague_lot_fill_asphalt_ortho2020_UNVERIFIED_edges',me)
    ob.users_collection[0].objects.link(fo)
    print('WS80a fill faces',len(me.polygons),flush=True)
# (3) lawn mask extended east: 0.5 m/px, x -350..-200, y -165..-55
fp=R+'data/ws80_sprague_lawn_mask.png'
mat=bpy.data.materials['WS68_Ground_ortho_grass_north2020']; N=mat.node_tree.nodes
N['WS75_mask'].image=bpy.data.images.load('//data/ws80_sprague_lawn_mask.png',check_existing=True)
N['WS75_mask'].image.colorspace_settings.name='Non-Color'
mp=N['WS75_map']; mp.inputs['Scale'].default_value=(1/150,1/110,1); mp.inputs['Location'].default_value=(350/150,165/110,0)
print('WS80a lawn mask ->',fp,flush=True)

bpy.ops.wm.save_mainfile()
print('WS80a SAVED',flush=True)
