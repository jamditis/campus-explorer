import bpy, numpy as np, os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
M='/workspace/nj-scenes/montclair-state/montclair_state.blend'
with bpy.data.libraries.load(M) as (a,b):
    b.objects=['Footpaths_OSM','Terrain_LiDAR_DTM_1m','Lawn_worn_edge_along_walks','CCOM_dock_apron_20261014jf3']
T={}
for o in b.objects:
    mw=o.matrix_world; T[o.name[:6]]=BVHTree.FromPolygons([mw@v.co for v in o.data.vertices],[tuple(p.vertices) for p in o.data.polygons])
def hz(t,x,y):
    h=t.ray_cast(Vector((x,y,160)),Vector((0,0,-1)),80); return h[0].z if h[0] is not None else None
for y in np.arange(-36,-58,-0.5):
    xs=np.arange(4,16,0.05); fp=[hz(T['Footpa'],x,y) for x in xs]; te=[hz(T['Terrai'],x,y) for x in xs]
    vis=[(f is not None and (t is None or f>t)) for f,t in zip(fp,te)]
    has=[f is not None for f in fp]
    idx=[i for i,v in enumerate(vis) if v]; hidx=[i for i,v in enumerate(has) if v]
    gaps=sum(1 for i in range(len(vis)-1) if vis[i]!=vis[i+1])
    print('E206 y%.1f fp x %.2f..%.2f  visible x %.2f..%.2f transitions %d  terr-fp at E edge %s'%(y,xs[hidx[0]] if hidx else 0,xs[hidx[-1]] if hidx else 0,xs[idx[0]] if idx else 0,xs[idx[-1]] if idx else 0,gaps,
      '%.3f'%(te[hidx[-1]]-fp[hidx[-1]]) if hidx and te[hidx[-1]] is not None else '-'))
