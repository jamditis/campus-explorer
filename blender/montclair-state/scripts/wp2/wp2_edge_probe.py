import bpy, json
from mathutils import Vector
segs=json.load(open('/workspace/nj-scenes/montclair-state/data/wo2/edge_streets_inside.json'))
ids=[s[1] for s in segs]
hits={}
for o in bpy.data.objects:
    n=o.name
    if any(i in n for i in ids) or 'Carlisle' in n or 'Webster' in n or 'Yogi' in n:
        hits.setdefault('named',[]).append(n)
# objects with bbox near each segment midpoint (roads collections)
for s in segs:
    a,b=Vector((*s[5],0)),Vector((*s[6],0)); m=(a+b)/2
    near=[]
    for o in bpy.data.objects:
        if o.type!='MESH' or not o.data.vertices: continue
        bb=[o.matrix_world@Vector(c) for c in o.bound_box]
        xs=[p.x for p in bb]; ys=[p.y for p in bb]
        if min(xs)-2<m.x<max(xs)+2 and min(ys)-2<m.y<max(ys)+2 and (max(xs)-min(xs))<800:
            near.append(o.name)
    hits[s[0]+' '+s[1]]=near[:12]
print('EDGE',json.dumps(hits)[:6000])
