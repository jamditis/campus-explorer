import bpy,bmesh,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
src='/workspace/nj-scenes/montclair-state/montclair_state.blend'
with bpy.data.libraries.load(src,link=False) as (fr,to):
    to.objects=[n for n in fr.objects if n=='Terrain_LiDAR_DTM_1m' or n.startswith('WS63_E_band_DTM') or n.startswith('QI_east_edge_delete')]
D=np.load('/workspace/nj-scenes/montclair-state/data/dtm_1m.npy'); print('SW D',D.shape)
for o in to.objects: bpy.context.scene.collection.objects.link(o)
dg=bpy.context.evaluated_depsgraph_get(); dg.update()
T=bpy.data.objects['Terrain_LiDAR_DTM_1m']; m=T.evaluated_get(dg).to_mesh(); bm=bmesh.new(); bm.from_mesh(m); bm.transform(T.matrix_world); BV=BVHTree.FromBMesh(bm)
# face size map: big faces
S=4; R=[]
for y in range(-246,247,S):
    for x in range(-246,247,S):
        h,n,i,d=BV.ray_cast(Vector((x,y,500)),Vector((0,0,-1)),1000)
        if h is None: continue
        a=bm.faces[i].calc_area() if False else m.polygons[i].area
        R.append((x,y,h.z-D[y+250,x+250],a))
R=np.array(R); np.save('data/ws64_sweep.npy',R)
bad=R[(np.abs(R[:,2])>1.0)]
print('SW samples',len(R),'|d|>1',len(bad),'big-face(>50m2)&|d|>1',int(((np.abs(R[:,2])>1)&(R[:,3]>50)).sum()))
