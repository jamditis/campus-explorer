import bpy,numpy as np
from mathutils.bvhtree import BVHTree
O=bpy.data.objects
for n in sorted(k for k in O.keys() if k.startswith('QT_soil_edge_')):
    t=O[n]; s=O.get(n.replace('QT_soil_edge_','QS_footway_'))
    if s is None: print('NOSLAB',n); continue
    sm=s.data; V=[s.matrix_world@v.co for v in sm.vertices]; B=BVHTree.FromPolygons(V,[tuple(p.vertices) for p in sm.polygons])
    d=np.array([B.find_nearest(t.matrix_world@v.co)[3] for v in t.data.vertices])
    print(n,len(t.data.vertices),len(t.data.polygons),'dist pct',np.percentile(d,[10,50,75,90,99]).round(3),'mat',[m.name for m in t.data.materials][:2],'mods',[m.type for m in t.modifiers],flush=True)
