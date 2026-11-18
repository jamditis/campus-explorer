import bpy,os,runpy
F='/workspace/nj-scenes/montclair-state/montclair_state.blend'
W=['MID_street_tree_proto_20261015ag','MID_canopy_carpet_SW_far_crowns_wq2','MID_canopy_carpet_far_crowns_ai','Context_skirt_3DEP_ortho_4km','Terrain_LiDAR_DTM_1m']
with bpy.data.libraries.load(F,link=False) as (s,d): d.objects=W+[n for n in s.objects if n.startswith('MID_stree_')]
for o in d.objects: bpy.context.scene.collection.objects.link(o)
runpy.run_path('/workspace/nj-scenes/montclair-state/scripts/ws48/band_build.py')

import bpy
from mathutils import Vector
from datetime import datetime
sc=bpy.context.scene
for o in sc.objects:
    if o.name.startswith('MID_stree_'): pass
print('B48 MID_stree objs',sum(1 for o in sc.objects if o.name.startswith('MID_stree_')))
