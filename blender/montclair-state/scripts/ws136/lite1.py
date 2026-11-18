import bpy
from mathutils import Vector
want=[n for n in open('/workspace/nj-scenes/montclair-state/scripts/ws136/names.txt').read().split('\n') if n.startswith(('WS134g_','UA_footway_312845863','WS135a_Skyline_Way_asphalt','WS135a_Skyline_W'))]
with bpy.data.libraries.load('/workspace/nj-scenes/montclair-state/montclair_state.blend') as (df,dt):
    dt.objects=want
for o in dt.objects:
    mw=o.matrix_world; vs=[mw@v.co for v in o.data.vertices]
    print(o.name,len(o.data.polygons),[round(min(getattr(v,a) for v in vs),1) for a in 'xyz'],[round(max(getattr(v,a) for v in vs),1) for a in 'xyz'])
