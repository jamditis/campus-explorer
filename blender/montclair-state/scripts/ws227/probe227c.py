import bpy, sys, os
from mathutils import Vector
o=bpy.data.objects['WS60_terrain_edge_apron_LiDAR_to_skirt']; t=bpy.data.objects['Terrain_LiDAR_DTM_1m']
print('P227C apron mods',[(m.name,m.type) for m in o.modifiers],flush=True)
for px,py in [(246.3,-248.7),(246.0,-33.5)]:
    near=sorted(((o.matrix_world@v.co) for v in o.data.vertices),key=lambda c:(c.x-px)**2+(c.y-py)**2)[:4]
    tn=sorted((v.co for v in t.data.vertices),key=lambda c:(c.x-px)**2+(c.y-py)**2)[:3]
    print('P227C apex',px,py,'apron',[tuple(round(q,2) for q in c) for c in near],'terrain',[tuple(round(q,2) for q in c) for c in tn],flush=True)
sys.stdout.flush(); os._exit(0)
