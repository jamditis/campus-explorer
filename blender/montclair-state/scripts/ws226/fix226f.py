# W53 part 3: deleting the giant base face (fix226a) uncovered 58 samples (2 m grid, probe226n) of see-through terrain
# along patch seams (106,78)->(158,152) and two small clusters: later patch modifiers delete earlier patch faces where
# their own patch has gaps, and the old base face used to back them. New backing object, nothing moved: for each hole
# sample a 6x6 m skin (1 m grid) whose vertices sit 8 cm under the evaluated terrain there (or under dtm_1m where the
# terrain misses), terrain ortho grass material + ortho UVs, so the slit reads as the surrounding ground.
import bpy, bmesh, json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
import numpy as np
A=np.load('/workspace/nj-scenes/montclair-state/data/dtm_1m.npy')
H=json.load(open('/workspace/nj-scenes/montclair-state/scripts/ws226/holes226.json'))
t=bpy.data.objects['Terrain_LiDAR_DTM_1m']
sv=[m.show_viewport for m in t.modifiers]
for m in t.modifiers: m.show_viewport=m.show_render
dg=bpy.context.evaluated_depsgraph_get(); e=t.evaluated_get(dg); tm=e.to_mesh()
B=BVHTree.FromPolygons([v.co.copy() for v in tm.vertices],[p.vertices[:] for p in tm.polygons]); e.to_mesh_clear()
for m,s in zip(t.modifiers,sv): m.show_viewport=s
def z(x,y):
    h=B.ray_cast(Vector((x,y,400)),Vector((0,0,-1)))
    return (h[0].z if h[0] else float(A[int(y+250),int(x+250)]))-0.08
cells=set()
for hx,hy in H:
    cx,cy=int(round(hx+0.3)),int(round(hy+0.3))
    for i in range(-3,3):
        for j in range(-3,3): cells.add((cx+i,cy+j))
bm=bmesh.new(); vv={}
def V(x,y):
    if (x,y) not in vv: vv[(x,y)]=bm.verts.new(Vector((x,y,z(x,y))))
    return vv[(x,y)]
for x,y in cells:
    f=bm.faces.new((V(x,y),V(x+1,y),V(x+1,y+1),V(x,y+1)))
me=bpy.data.meshes.new('WS226_east_patch_seam_backing'); bm.to_mesh(me); bm.free()
uv=me.uv_layers.new(name='ortho')
for l in me.loops:
    c=me.vertices[l.vertex_index].co; uv.data[l.index].uv=((c.x+250)/500,(c.y+250)/500)
for p in me.polygons: p.use_smooth=True
nm='WS226_east_patch_seam_backing_UNVERIFIED'
if nm in bpy.data.objects: bpy.data.objects.remove(bpy.data.objects[nm])
o=bpy.data.objects.new(nm,me); o.data.materials.append(t.data.materials[0])
for c in t.users_collection: c.objects.link(o)
print('F226F backing cells',len(me.polygons),'m2',round(sum(p.area for p in me.polygons)),flush=True)
