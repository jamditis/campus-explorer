import bpy,numpy as np
from mathutils.bvhtree import BVHTree
O=bpy.data.objects
for n in sorted(k for k in O.keys() if 'soil_edge' in k and not k.startswith('QT_')):
    t=O[n]; cand=[n.replace('soil_edge','footway'), n.replace('_soil_edge_','_footway_')]
    s=next((O[c] for c in cand if c in O),None)
    if s is None or t.type!='MESH': print('NOSLAB',n,flush=True); continue
    V=[s.matrix_world@v.co for v in s.data.vertices]; B=BVHTree.FromPolygons(V,[tuple(p.vertices) for p in s.data.polygons])
    D=np.array([B.find_nearest(t.matrix_world@v.co)[3] for v in t.data.vertices])
    print('Q',n,s.name,len(D),np.histogram(D,bins=[0,0.05,0.09,0.13,0.17,0.21,0.25,0.35,9])[0],flush=True)
