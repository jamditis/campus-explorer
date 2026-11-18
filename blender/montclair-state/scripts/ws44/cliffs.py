import bpy,bmesh,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from collections import defaultdict
dg=bpy.context.evaluated_depsgraph_get()
ob=bpy.data.objects['Terrain_LiDAR_DTM_1m']; bm=bmesh.new(); bm.from_mesh(ob.evaluated_get(dg).to_mesh()); bm.transform(ob.matrix_world); T=BVHTree.FromBMesh(bm)
xs=np.arange(-200,140,0.5); ys=np.arange(-130,130,0.5); Z=np.full((len(ys),len(xs)),np.nan)
for j,y in enumerate(ys):
    for i,x in enumerate(xs):
        r=T.ray_cast(Vector((x,y,300)),Vector((0,0,-1)),600)
        if r[0]: Z[j,i]=r[0].z
gy,gx=np.gradient(Z,0.5); S=np.degrees(np.arctan(np.hypot(gx,gy)))
np.save('/workspace/nj-scenes/montclair-state/scripts/ws44/Z.npy',Z)
c=defaultdict(list)
for j,i in zip(*np.where(S>40)):
    x,y=xs[i],ys[j]
    h=bpy.context.scene.ray_cast(dg,Vector((x,y,Z[j,i]+40)),Vector((0,0,-1)))
    if h[0] and h[4].name!='Terrain_LiDAR_DTM_1m' and h[1].z>Z[j,i]-0.02: continue  # covered
    c[(int(x//5*5),int(y//5*5))].append(S[j,i])
print('CL cells',len(c))
for k,v in sorted(c.items(),key=lambda kv:-len(kv[1]))[:30]: print('CL',k,len(v),round(max(v)))
