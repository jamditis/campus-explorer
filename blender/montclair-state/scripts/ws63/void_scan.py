import bpy,bmesh,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
T=bpy.data.objects['Terrain_LiDAR_DTM_1m']; dg=bpy.context.evaluated_depsgraph_get()
m=T.evaluated_get(dg).to_mesh(); bm=bmesh.new(); bm.from_mesh(m); BV=BVHTree.FromBMesh(bm)
miss=[];back=[]
for y in np.arange(-68,-54,0.05):
    for x in np.arange(92,115,0.05):
        h,n,i,d=BV.ray_cast(Vector((x,y,400)),Vector((0,0,-1)),1000)
        if h is None: miss.append((x,y))
        elif n.z<0: back.append((round(x,1),round(y,1)))
print('VS miss',len(miss),miss[:8]); print('VS back',len(back),back[:12])
# open boundary edges in box
be=[e for e in bm.edges if e.is_boundary and all(80<v.co.x<152 and -90<v.co.y<-48 for v in e.verts)]
print('VS boundary edges in box',len(be),[tuple(round(c,1) for c in e.verts[0].co) for e in be[:10]])
