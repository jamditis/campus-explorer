import bpy, math
from mathutils import Vector
with bpy.data.libraries.load('/workspace/nj-scenes/montclair-state/montclair_state.blend') as (df,dt):
    dt.objects=['Footpaths_OSM']
o=dt.objects[0]; mw=o.matrix_world
import collections
cells=collections.defaultdict(list)
for p in o.data.polygons:
    c=mw@p.center
    if -135<c.x<-105 and -272<c.y<-205: cells[(int((c.y+272)//3),int((c.x+135)//1.5))].append(c.z)
for yi in range(22,-1,-1):
    print('%6.0f '%(-272+yi*3)+''.join('#' if (yi,xi) in cells else '.' for xi in range(20)))
print('x from -135 step 1.5')
