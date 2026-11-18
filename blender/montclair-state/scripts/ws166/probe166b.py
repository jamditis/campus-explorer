import bpy, os
M='/workspace/nj-scenes/montclair-state/montclair_state.blend'
want=lambda n: n.startswith(('WS110_ground','WS163_','WS164_','WS165_'))
with bpy.data.libraries.load(M) as (s,d): d.objects=[n for n in s.objects if want(n)]
for o in d.objects:
    if o: bpy.context.scene.collection.objects.link(o)
print('LOADED',len(d.objects),flush=True)
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws166/hdr166.py').read())
import numpy as np
from collections import Counter
def scan(tag):
    bpy.context.view_layer.update(); dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene; C=Counter(); ex={}
    for x in np.arange(XW-0.1,XE+0.3,0.05):
        for y in np.arange(wb(x)-0.1,YN+0.1,0.05):
            r=sc.ray_cast(dg,Vector((x,y,300)),Vector((0,0,-1)))
            if not r[0]: continue
            n=r[4].name; C[n[:40]]+=1
            if inside(min(max(x,xi0),XE),y) and not n.startswith(('WS165_aisle','WS165_concrete','WS164_aisle_mouth_curb','WS164_')): ex.setdefault(n[:40],[]).append((round(x,2),round(y,2)))
    print(tag,'HITS',dict(C),flush=True)
    for k,v in ex.items(): print(tag,'INSIDE-BED non-mulch',k,len(v),v[:8],flush=True)
scan('BEFORE')
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws166/fix166.py').read())
scan('AFTER')
