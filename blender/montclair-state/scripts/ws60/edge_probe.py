import bpy,bmesh,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
N=['Terrain_LiDAR_DTM_1m','Context_skirt_3DEP_ortho_4km']
with bpy.data.libraries.load('/workspace/nj-scenes/montclair-state/montclair_state.blend',link=False) as (s,d): d.objects=[n for n in N if n in s.objects]
for o in d.objects: bpy.context.scene.collection.objects.link(o)
dg=bpy.context.evaluated_depsgraph_get()
def tr(n):
    o=bpy.data.objects[n]; bm=bmesh.new(); bm.from_mesh(o.evaluated_get(dg).to_mesh()); bm.transform(o.matrix_world); return BVHTree.FromBMesh(bm),bm
T,tb=tr(N[0]); S,sb=tr(N[1])
xs=[v.co.x for v in tb.verts]; ys=[v.co.y for v in tb.verts]
print('E60 terrain bbox',round(min(xs)),round(max(xs)),round(min(ys)),round(max(ys)))
# boundary edges of terrain: gap to skirt
gaps=[]
for e in tb.edges:
    if e.is_boundary:
        p=(e.verts[0].co+e.verts[1].co)/2
        r=S.ray_cast(Vector((p.x,p.y,p.z+50)),Vector((0,0,-1)),200)
        if r[0]: gaps.append((round(p.z-r[0].z,2),round(p.x),round(p.y)))
gaps.sort(); print('E60 n',len(gaps),'lowest',gaps[:5],'highest',gaps[-12:])
import collections
big=[g for g in gaps if g[0]>0.5]; c=collections.Counter((g[1]//50*50,g[2]//50*50) for g in big); print('E60 >0.5m cells',c.most_common(12))
