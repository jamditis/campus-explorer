# Builds a small hidden-under-terrain filler mesh for the 0.7 m2 SE seam voids (x 88-102, y -62..-48)
import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
F='/workspace/nj-scenes/montclair-state/montclair_state.blend'
with bpy.data.libraries.load(F,link=False) as (s,d): d.objects=['Terrain_LiDAR_DTM_1m']
o=d.objects[0]; bpy.context.scene.collection.objects.link(o)
dg=bpy.context.evaluated_depsgraph_get(); m=o.evaluated_get(dg).to_mesh(); bm=bmesh.new(); bm.from_mesh(m); bm.transform(o.matrix_world); T=BVHTree.FromBMesh(bm)
def hit(x,y):
    h=T.ray_cast(Vector((x,y,300)),Vector((0,0,-1)))[0]; return h.z if (h is not None and h.z>50) else None
miss=[]
x=88.0
while x<102:
    y=-62.0
    while y<-48:
        if hit(x,y) is None: miss.append((x,y))
        y+=0.1
    x+=0.1
S=0.5; cells=set()
for a,b in miss:
    for dx in (-1,0,1):
        for dy in (-1,0,1): cells.add((int((a//S))+dx,int((b//S))+dy))
def zat(x,y):
    z=hit(x,y)
    if z is not None: return z
    best=None
    for r in (0.3,0.6,1.0,1.5,2.5):
        vals=[hit(x+dx*r,y+dy*r) for dx,dy in ((1,0),(-1,0),(0,1),(0,-1),(.7,.7),(-.7,.7),(.7,-.7),(-.7,-.7))]
        vals=[v for v in vals if v is not None]
        if vals: return sum(vals)/len(vals)
    return None
nb=bmesh.new(); V={}
def vert(i,j):
    if (i,j) not in V:
        z=zat(i*S,j*S); V[(i,j)]=nb.verts.new((i*S,j*S,(z if z is not None else 108.0)-0.04))
    return V[(i,j)]
for i,j in cells: nb.faces.new((vert(i,j),vert(i+1,j),vert(i+1,j+1),vert(i,j+1)))
me=bpy.data.meshes.new('WS50_SE_seam_filler'); nb.to_mesh(me)
for p in me.polygons: p.use_smooth=True
f=bpy.data.objects.new('WS50_SE_seam_filler',me)
bpy.data.libraries.write('/workspace/nj-scenes/montclair-state/data/ws50/se_seam_filler.blend',{f},fake_user=True)
print('F50 misses',len(miss),'cells',len(cells),'verts',len(me.vertices))
