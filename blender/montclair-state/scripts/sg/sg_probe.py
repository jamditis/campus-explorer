import bpy,json
from mathutils import Vector
dg=bpy.context.evaluated_depsgraph_get()
W=json.load(open('data/sf/north_lot_osm.json'))['ways']
road=W['313028548']['pts'][::-1]+W['313028549']['pts'][1:]
# objects whose bbox touches the road path beyond x>75 or x<-75
for o in bpy.data.objects:
    if o.type!='MESH' or o.hide_render: continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    x0=min(b.x for b in bb);x1=max(b.x for b in bb);y0=min(b.y for b in bb);y1=max(b.y for b in bb)
    if x1-x0>2000: continue
    for (x,y) in [(-83,369.6),(-78,365),(90,341),(114.7,330.2),(139,319),(148,315.6)]:
        if x0<x<x1 and y0<y<y1 and ('oad' in o.name or 'sphalt' in o.name or 'Foot' in o.name or 'walk' in o.name.lower() or 'SF_' in o.name):
            print('HIT',(x,y),o.name); 
LOT=W['313028558']['pts']
print('LOT',[tuple(round(c,1) for c in p) for p in LOT])
for n in ['Roads_OSM']:
    o=bpy.data.objects.get(n); print(n, o and len(o.data.vertices))
