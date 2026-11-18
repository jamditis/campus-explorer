# ws80b: smooth the WS80 fill's outer outline (0.4 m stair steps at the traced polygon) and re-drape; mask PNG regenerated (+0.8 m under the lot edge)
import bpy,bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
P=[(-264,-86),(-264,-95.5),(-230.3,-108.3),(-230.3,-127),(-229,-130.5),(-224,-131),(-221.5,-128),(-220.3,-120),(-219.8,-110),(-217.5,-108),(-216.5,-96),(-216.5,-86)]
def dseg(px,py):
    best=9e9; n=len(P)
    for i in range(n):
        (x1,y1),(x2,y2)=P[i],P[(i+1)%n]; dx,dy=x2-x1,y2-y1; L=dx*dx+dy*dy
        t=max(0,min(1,((px-x1)*dx+(py-y1)*dy)/L)); qx,qy=x1+t*dx,y1+t*dy; d=((px-qx)**2+(py-qy)**2)**.5
        if d<best: best,bq=d,(qx,qy)
    return best,bq
dg=bpy.context.evaluated_depsgraph_get()
def bvh(o):
    oe=o.evaluated_get(dg); m=oe.to_mesh(); b=bmesh.new(); b.from_mesh(m); b.transform(o.matrix_world); t=BVHTree.FromBMesh(b); b.free(); oe.to_mesh_clear(); return t
TG=[bvh(o) for o in bpy.data.objects if o.name.startswith('WS68_RHD_ground') or o.name=='Terrain_LiDAR_DTM_1m']
def gz(x,y):
    zs=[h[0].z for h in (t.ray_cast(Vector((x,y,300)),Vector((0,0,-1))) for t in TG) if h[0]]
    return max(zs) if zs else None
for nm in ('WS80_sprague_lot_fill_asphalt_ortho2020_UNVERIFIED_edges','WS75_sprague_lot_asphalt_ortho2020_UNVERIFIED_edges'):
    ob=bpy.data.objects[nm]; bm=bmesh.new(); bm.from_mesh(ob.data)
    outer=[v for v in bm.verts if v.is_boundary and v.co.y<-90 and dseg(v.co.x,v.co.y)[0]<0.75]
    # snap outer outline verts onto the traced polygon (removes 0.4 m stair steps), then 1 smoothing pass
    for v in outer:
        d,q=dseg(v.co.x,v.co.y); v.co.x,v.co.y=q
    new={}
    for v in outer:
        nb=[e.other_vert(v) for e in v.link_edges if e.is_boundary]
        if len(nb)==2: new[v]=(v.co.xy*0.5+(nb[0].co.xy+nb[1].co.xy)*0.25)
    for v,c in new.items(): v.co.x,v.co.y=c.x,c.y
    for v in outer:
        g=gz(v.co.x,v.co.y)
        if g is not None: v.co.z=g+(0.04 if nm.startswith('WS80') else 0.045)
    bm.to_mesh(ob.data); bm.free(); ob.data.update()
    print('WS80b',nm[:20],'outline verts snapped',len(outer),flush=True)
im=bpy.data.images.get('ws80_sprague_lawn_mask.png')
if im: im.reload()
bpy.ops.wm.save_mainfile(); print('WS80b SAVED',flush=True)
