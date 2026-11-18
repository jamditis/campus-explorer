"""wo probe2: 1 m coverage map of LiDAR ground objects vs 3DEP skirt in x40-260,y140-335; dz skirt vs 2017 DTM in the uncovered cells."""
import bpy, json, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R='/workspace/nj-scenes/montclair-state'
dg=bpy.context.evaluated_depsgraph_get()
def bvh(n):
    o=bpy.data.objects[n];e=o.evaluated_get(dg);m=e.to_mesh();vs=[o.matrix_world@v.co for v in m.vertices];b=BVHTree.FromPolygons(vs,[tuple(p.vertices) for p in m.polygons]);e.to_mesh_clear();return b
G=['Terrain_LiDAR_DTM_1m','RZ2_SC_LiDAR_ground_patch_UNVERIFIED','WF_east_dorm_LiDAR_terrain_patch_UNVERIFIED','WJ_south_gully_LiDAR_patch_ext_UNVERIFIED','WN_south_wood_LiDAR_patch_ext_UNVERIFIED']
G+= [o.name for o in bpy.data.objects if o.type=='MESH' and ('LiDAR' in o.name and ('patch' in o.name.lower() or 'terrain' in o.name.lower() or 'ground' in o.name.lower())) and o.name not in G]
print('GROUNDS',G)
B={n:bvh(n) for n in G}
SK=bvh('Context_skirt_3DEP_ortho_4km')
g=np.load(f'{R}/data/wo/chm_grid_sw_1m.npz'); kd=[f for f in g.files if 'J5D6' in f and f.endswith('dtm')][0]; D=g[kd]
X0,Y0=40,140; ny,nx=D.shape
cov=np.zeros((ny,nx),np.int16); skz=np.full((ny,nx),np.nan); gz=np.full((ny,nx),np.nan)
for j in range(ny):
    for i in range(nx):
        p=Vector((X0+i+0.5,Y0+j+0.5,600))
        best=None
        for k,n in enumerate(G):
            h=B[n].ray_cast(p,Vector((0,0,-1)))
            if h[0] is not None and (best is None or h[0].z>best[1]): best=(k+1,h[0].z)
        if best: cov[j,i]=best[0]; gz[j,i]=best[1]
        h=SK.ray_cast(p,Vector((0,0,-1)))
        if h[0] is not None: skz[j,i]=h[0].z
np.savez_compressed(f'{R}/data/wo/coverage.npz',cov=cov,skz=skz,gz=gz,names=np.array(G))
for j in range(ny-1,-1,-5):
    print(Y0+j,''.join('.' if cov[j,i]==0 else str(cov[j,i]%10) for i in range(0,nx,3)))
u=(cov==0)&np.isfinite(D)&np.isfinite(skz)
d=D[u]-skz[u]
print('UNCOV',int((cov==0).sum()),'with dtm',int(u.sum()),'dz pct',np.percentile(d,[5,25,50,75,95]).round(2) if u.any() else None)
