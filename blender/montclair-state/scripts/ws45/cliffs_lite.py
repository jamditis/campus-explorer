import bpy,bmesh,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from collections import defaultdict
src='/workspace/nj-scenes/montclair-state/montclair_state.blend'
with bpy.data.libraries.load(src,link=False) as (fr,to): to.objects=['Terrain_LiDAR_DTM_1m']
o=to.objects[0]; bpy.context.scene.collection.objects.link(o)
print('CL mods',[m.name for m in o.modifiers],len(o.data.vertices))
dg=bpy.context.evaluated_depsgraph_get()
bm=bmesh.new(); bm.from_mesh(o.evaluated_get(dg).to_mesh()); bm.transform(o.matrix_world); T=BVHTree.FromBMesh(bm)
xs=np.arange(-200,140,0.5); ys=np.arange(-130,130,0.5); Z=np.full((len(ys),len(xs)),np.nan)
for j,y in enumerate(ys):
    for i,x in enumerate(xs):
        r=T.ray_cast(Vector((x,y,300)),Vector((0,0,-1)),600)
        if r[0]: Z[j,i]=r[0].z
np.save('/workspace/nj-scenes/montclair-state/scripts/ws45/Z.npy',Z); print('CL saved')
