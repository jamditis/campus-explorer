import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
T=bpy.data.objects['Terrain_LiDAR_DTM_1m']; tm=T.matrix_world
tv=[tm@v.co for v in T.data.vertices]
ins=[-290<=v.x<=-180 and 130<=v.y<=250 for v in tv]
polys=[list(p.vertices) for p in T.data.polygons if any(ins[i] for i in p.vertices)]
used=sorted({i for p in polys for i in p}); rm={o:n for n,o in enumerate(used)}
bt=BVHTree.FromPolygons([tv[i] for i in used],[[rm[i] for i in p] for p in polys])
for x,y in [(-244,190),(-240,200),(-230,160),(-244.5,150),(-244.5,230),(-200,200)]:
    h=bt.ray_cast(Vector((x+0.5,y+0.5,300)),Vector((0,0,-1)),400); print('PT',x,y,round(h[0].z,2) if h[0] else None)
print('TMOD',[m.name for m in T.modifiers])
