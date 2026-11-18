import bpy, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
dg=bpy.context.evaluated_depsgraph_get()
def ev(o):
    e=o.evaluated_get(dg); me=e.to_mesh(); mw=o.matrix_world
    b=BVHTree.FromPolygons([tuple(mw@v.co) for v in me.vertices],[tuple(p.vertices) for p in me.polygons]); e.to_mesh_clear(); return b
G=[(o.name,ev(o)) for o in bpy.data.objects if o.type=='MESH' and o.name.startswith(('Terrain_LiDAR','WS113_terrain','WS110_ground'))]
P=[ev(o) for o in bpy.data.objects if o.type=='MESH' and o.name.startswith(('WS117_Chapin_W_entrance_stair_11R','WS117_Chapin_W_entrance_landing'))]
bad=0;N=0;worst=0;where=[]
for x in np.arange(-217.0,-208.0,0.25):
  for y in np.arange(-201.2,-181.5,0.25):
    zs=[h[0].z for h in (b.ray_cast(Vector((x,y,200)),Vector((0,0,-1)),150) for b in P) if h[0] is not None]
    if not zs: continue
    N+=1; zw=max(zs)
    for nm,g in G:
        hg=g.ray_cast(Vector((x,y,200)),Vector((0,0,-1)),150)
        if hg[0] is not None and hg[0].z>zw-0.005:
            bad+=1; dz=hg[0].z-zw
            if dz>worst: worst=dz; where=(round(x,2),round(y,2),nm[:30])
print('Q6_118 samples',N,'terrain over stair/landing',bad,'worst %.3f'%worst,where)
