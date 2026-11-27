# ws262 M4b (merge208 CHAIN): make every ID that main links from //north/sprague_cafe_src.blend LOCAL (one-file merge: main must not
# depend on north/), then drop the empty Library datablock. Order = users first (collections -> objects -> data -> materials ->
# node groups -> images), repeated until nothing changes, so every ID only has local users when it is localised (made local in
# place, no copies; ws262 first try leaves-first copied a few and left 1,127 linked -> rejected). Census262c: 649 objects, 383 meshes, 87 materials, 21 collections,
# 4 lights, 2 node groups, 1 image. merge208's _OFF (object name, modifier) list is re-keyed by pointer so the
# Realtime-bit restore still finds objects if localising renames them.
import bpy, os
TAG='F262C'; LIB=[l for l in bpy.data.libraries if l.filepath.replace('\\','/').endswith('north/sprague_cafe_src.blend')]
if not LIB: raise SystemExit('F262C no sprague lib (already local?)')
LIB=LIB[0]
def ids():
    out=[]
    for attr in ('collections','objects','meshes','curves','lights','cameras','fonts','materials','node_groups','textures','images'):
        out+=[(attr,i) for i in getattr(bpy.data,attr) if i.library==LIB]
    return out
before=ids(); print(TAG,'linked ids',len(before),flush=True)
lnames={i.name for a,i in before if a=='objects'}
coll=[n for n in lnames if any(o.name==n and o.library is None for o in bpy.data.objects)]
print(TAG,'name collisions with local objects',len(coll),coll[:5],flush=True)
ptr={}  # pointer -> list of _OFF indices
for k,(on,mn) in enumerate(_OFF):
    for o in bpy.data.objects:
        if o.name==on and mn in o.modifiers: ptr.setdefault(o.as_pointer(),[]).append(k)
n=0; cp=0
for ps in range(8):
    cur=ids()
    if not cur: break
    for attr,i in cur:
        try:
            j=i.make_local(); n+=1
            if j is not None and j!=i: cp+=1
        except Exception as e: print(TAG,'FAIL',attr,i.name,e,flush=True)
    print(TAG,'pass',ps,'was',len(cur),'now',len(ids()),flush=True)
print(TAG,'copies (should be 0)',cp,flush=True)
left=ids(); print(TAG,'made local',n,'left linked',len(left),[i.name for a,i in left][:8],flush=True)
# re-key _OFF
byp={o.as_pointer():o for o in bpy.data.objects}; rk=0
for p,ks in ptr.items():
    o=byp.get(p)
    if o is None: print(TAG,'OFF object pointer gone',[_OFF[k] for k in ks][:2],flush=True); continue
    for k in ks:
        if _OFF[k][0]!=o.name: _OFF[k]=(o.name,_OFF[k][1]); rk+=1
print(TAG,'OFF re-keyed',rk,flush=True)
if not left and LIB.users==0:
    bpy.data.libraries.remove(LIB); print(TAG,'library removed',flush=True)
else: print(TAG,'library kept users',LIB.users,flush=True)
print(TAG,'libraries now',[l.name for l in bpy.data.libraries],flush=True)
