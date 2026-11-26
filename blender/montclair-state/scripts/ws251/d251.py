# ws251 read-only: evaluated Terrain (incl. joined W63 patch) minus 2023 LiDAR (2017+0.12 fallback), 1 m, x -204..-170, y 128..184
import bpy, os, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
F='/workspace/nj-scenes/montclair-state/'+os.environ.get('F','montclair_state.blend')
with bpy.data.libraries.load(F) as (a,b): b.objects=['Terrain_LiDAR_DTM_1m','WS250_W63_lawn_LiDAR2023_ground_patch_1m']
T=b.objects[0]
for o in b.objects: bpy.context.scene.collection.objects.link(o)
dg=bpy.context.evaluated_depsgraph_get(); em=T.evaluated_get(dg).to_mesh(); M=T.matrix_world
vs=[M@v.co for v in em.vertices]
ps=[p.vertices[:] for p in em.polygons if any(-260<vs[i].x<-120 and 100<vs[i].y<220 for i in p.vertices)]
bvh=BVHTree.FromPolygons(vs,ps)
D='/workspace/nj-scenes/montclair-state/scripts/ws248/'
G23=np.load(D+'g1m_23.npy'); G17=np.load(D+'g1m_17.npy'); X0,Y0=-320.,-20.
xs=np.arange(-204,-169); ys=np.arange(128,185)
O=np.full((len(ys),len(xs)),np.nan); L=np.full_like(O,np.nan); C=np.zeros_like(O)
for j,y in enumerate(ys):
    for i,x in enumerate(xs):
        h=bvh.ray_cast(Vector((x+0.5,y+0.5,400)),Vector((0,0,-1)),600)
        if h[0]: O[j,i]=h[0].z
        a=G23[int(y-Y0),int(x-X0)]; b_=G17[int(y-Y0),int(x-X0)]
        L[j,i]=a if np.isfinite(a) else (b_+0.12 if np.isfinite(b_) else np.nan); C[j,i]=1 if np.isfinite(a) else (2 if np.isfinite(b_) else 0)
np.save('d251.npy',np.stack([O,L,C]))
print('D251 cols x',xs[0],'..',xs[-1])
for j in range(len(ys)-1,-1,-1,):
    print('D251 y%4d '%ys[j]+''.join(('%5.1f'%(O[j,i]-L[j,i])) if np.isfinite(O[j,i]-L[j,i]) else ('   L ' if np.isfinite(O[j,i]) else '   . ') for i in range(len(xs))),flush=True)
os._exit(0)
