import bpy,bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
src='/workspace/nj-scenes/montclair-state/montclair_state.blend'
with bpy.data.libraries.load(src,link=False) as (fr,to): to.objects=['Terrain_LiDAR_DTM_1m']
o=to.objects[0]; bpy.context.scene.collection.objects.link(o)
for m in o.modifiers:
    print('MT mod',m.name,m.type,getattr(m,'object',None) and m.object.name, m.show_render, m.show_viewport)
pts=[(x,y) for x in range(94,140,3) for y in range(-74,-58,2)]
def run(tag):
    dg=bpy.context.evaluated_depsgraph_get()
    bm=bmesh.new(); bm.from_mesh(o.evaluated_get(dg).to_mesh()); bm.transform(o.matrix_world); T=BVHTree.FromBMesh(bm)
    miss=sum(1 for x,y in pts if not T.ray_cast(Vector((x,y,300)),Vector((0,0,-1)),600)[0])
    print('MT',tag,'miss',miss,'of',len(pts),'verts',len(bm.verts))
run('all')
# base mesh only
bm=bmesh.new(); bm.from_mesh(o.data); bm.transform(o.matrix_world); T=BVHTree.FromBMesh(bm)
print('MT base miss',sum(1 for x,y in pts if not T.ray_cast(Vector((x,y,300)),Vector((0,0,-1)),600)[0]))
for m in o.modifiers:
    m.show_viewport=False; run('without '+m.name); m.show_viewport=True
