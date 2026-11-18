import bpy
A='/workspace/nj-scenes/montclair-state/montclair_state_pre_20261113ws105.blend'
with bpy.data.libraries.load(A) as (s,d):
    names=[n for n in s.objects if n in ('Footpaths_OSM','Terrain_LiDAR_DTM_1m') or n.startswith('WS103_CollegeAve_S_W_sidewalk') or n.startswith('WS99_bed_shrub_') or 'Chapin' in n or n.startswith('WS102_')]
    d.objects=names
print('DRY appended',names)
for o in d.objects:
    if o: bpy.context.scene.collection.objects.link(o)
exec(compile(open('/workspace/nj-scenes/montclair-state/scripts/ws105/build105.py').read(),'build105','exec'))
import numpy as np
from mathutils import Vector
for o in bpy.data.objects:
    if 'Chapin' in o.name and not o.name.startswith('WS105'):
        bb=[o.matrix_world@Vector(c) for c in o.bound_box]
        so_=[so(np.array([v.x,v.y])) for v in bb]
        print('CH',o.name,'s',min(a for a,b in so_),max(a for a,b in so_),'o',min(b for a,b in so_),max(b for a,b in so_),'z',min(v.z for v in bb))
bpy.ops.wm.save_as_mainfile(filepath='/workspace/nj-scenes/montclair-state/scripts/ws105/dry106.blend')
print('DRY saved')
