import bpy, json, time
from mathutils import Vector
p='/workspace/nj-scenes/montclair-state/montclair_state.blend'
with bpy.data.libraries.load(p) as (s,d): allnames=list(s.objects)
print('I99 total',len(allnames)); inv={}; t=time.time()
B=150
for k in range(0,len(allnames),B):
    batch=allnames[k:k+B]
    with bpy.data.libraries.load(p) as (s,d): d.objects=batch
    for o in d.objects:
        if o is None: continue
        mw=o.matrix_world
        try:
            pts=[mw@Vector(c) for c in o.bound_box]
            inv[o.name]=[o.type,min(q.x for q in pts),max(q.x for q in pts),min(q.y for q in pts),max(q.y for q in pts),min(q.z for q in pts),max(q.z for q in pts),o.parent.name if o.parent else None]
        except Exception as e: inv[o.name]=[o.type,None]
    for o in list(bpy.data.objects): bpy.data.objects.remove(o)
    bpy.data.orphans_purge(do_recursive=True)
    if k%1500==0: print('I99',k,round(time.time()-t))
json.dump(inv,open('/workspace/nj-scenes/montclair-state/scripts/ws99/inventory99.json','w'))
print('I99 DONE',len(inv))
