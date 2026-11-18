import bpy, os
M='/workspace/nj-scenes/montclair-state/montclair_state_ws165a.blend'
want=lambda n: n.startswith(('WS110_ground','WS163_','WS164_','WS165_'))
with bpy.data.libraries.load(M) as (s,d): d.objects=[n for n in s.objects if want(n)]
for o in d.objects:
    if o: bpy.context.scene.collection.objects.link(o)
print('LOADED',len(d.objects),flush=True)
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws165/fix165b.py').read())
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws165/fix165c.py').read())
# check: lawn above mulch anywhere?
from mathutils.bvhtree import BVHTree
mu=bpy.data.objects['WS165_aisle_mouth_mulch_bed_graded_to_walk_UNIFY69']
TG=bvh([pa,gp]); TM=bvh([mu]); bad=0; n=0
for x in np.arange(-305.2,-300.05,0.1):
    for y in np.arange(-254,-249,0.1):
        if not inside(x,y): continue
        a=hz(TM,x,y); b=hz(TG,x,y); n+=1
        if a is None: bad+=1; continue
        if b is not None and b>a-0.005: bad+=1
print('CHECK pts',n,'bad',bad,flush=True)
from collections import Counter
C=Counter()
for x in np.arange(-305.2,-300.05,0.1):
    for y in np.arange(-254,-249,0.1):
        if not inside(x,y): continue
        a=hz(TM,x,y); b=hz(TG,x,y)
        if a is None: C[('none',round(x),round(fdist(x,y),1))]+=1
        elif b is not None and b>a-0.005: C[('above',round(x),round(fdist(x,y),1),round(b-a,3))]+=1
print(sorted(C.items())[:40])
