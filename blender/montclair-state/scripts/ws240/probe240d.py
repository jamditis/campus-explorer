# subset-render tool check: objects in main missing from ws205/bbox205.json (stale since ws216) -> they never render in subset WIPs
import bpy, json
from mathutils import Vector
B=json.load(open('/workspace/nj-scenes/montclair-state/scripts/ws205/bbox205.json'))
keys=set(B.keys()) if isinstance(B,dict) else set(x[0] for x in B)
miss={}
for o in bpy.data.objects:
    if o.name in keys or o.library or o.type not in ('MESH','CURVE','EMPTY','FONT'): continue
    w=[o.matrix_world@Vector(c) for c in o.bound_box]
    miss[o.name]=[min(v.x for v in w),max(v.x for v in w),min(v.y for v in w),max(v.y for v in w),o.type,o.hide_render]
json.dump(miss,open('/workspace/nj-scenes/montclair-state/scripts/ws240/bbox_missing240.json','w'),indent=0)
print('P240D missing',len(miss),[n[:40] for n,v in miss.items() if not v[5]][:80],flush=True)
