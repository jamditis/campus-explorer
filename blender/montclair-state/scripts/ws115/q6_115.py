import bpy, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
A=np.array([-235.4,-235.3]);B=np.array([-222.0,-197.4]);d=(B-A)/np.linalg.norm(B-A);n=np.array([-d[1],d[0]])
dg=bpy.context.evaluated_depsgraph_get()
def ev(o):
    e=o.evaluated_get(dg); me=e.to_mesh(); mw=o.matrix_world
    b=BVHTree.FromPolygons([tuple(mw@v.co) for v in me.vertices],[tuple(p.vertices) for p in me.polygons]); e.to_mesh_clear(); return b
G=[ev(o) for o in bpy.data.objects if o.type=='MESH' and o.name.startswith(('Terrain_LiDAR','WS113_terrain','WS110_ground'))]
wk=next(o for o in bpy.data.objects if o.name.startswith('WS115_E_walk')); bw=ev(wk)
bad=0;N=0;worst=0
for s in np.arange(0.2,34.5,0.5):
    for t in (-0.9,-0.45,0,0.45,0.9):
        p=A+d*s+n*t; h=bw.ray_cast(Vector((p[0],p[1],200)),Vector((0,0,-1)),150)
        if h[0] is None: continue
        N+=1; zw=h[0].z
        for g in G:
            hg=g.ray_cast(Vector((p[0],p[1],200)),Vector((0,0,-1)),150)
            if hg[0] is not None and hg[0].z>zw-0.005: bad+=1; worst=max(worst,hg[0].z-zw)
print('Q6_115 samples',N,'terrain over walk',bad,'worst %.3f'%worst)
