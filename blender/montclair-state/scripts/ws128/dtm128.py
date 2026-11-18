import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
P='/workspace/nj-scenes/montclair-state/scripts/ws127/cut127.blend'
with bpy.data.libraries.load(P) as (df,dt):
    dt.objects=[n for n in df.objects if n.startswith(('Terrain_LiDAR_DTM_1m',))]
o=dt.objects[0]; mw=o.matrix_world
V=[mw@v.co for v in o.data.vertices]
pts=[v for v in V if -247<v.x<-229 and -247<v.y<-231]
print('N',len(pts))
for y in range(-246,-232,2):
    row=sorted([v for v in pts if abs(v.y-y)<0.51],key=lambda v:v.x)
    print(y,' '.join('%.0f:%.2f'%(v.x,v.z) for v in row))
