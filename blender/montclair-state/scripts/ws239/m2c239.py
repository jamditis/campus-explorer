# ws239 ONE-SCENE M2 batch (c), first slice: Red Hawk Deck SE entrance detail (photo-based, built in north against the same
# Red Hawk Deck model main already carries as WS66_RedHawkDeck_from_north; probe: every shared SE-core object is identical in
# both files, so these fit main's own design). Appends from north/montclair_north.blend into NORTH_MERGE/N_site_detail_rhd:
# KX_rhd_entrance (RED HAWK DECK letters, P sign, photo-verified globe lamp), KX2 SE-block diamond grilles + openings,
# LA SE-core door set (maroon single door + sidelight, piers, push bar, wall light/conduit), KY clearance bar + 2 hangers
# (the bar was SKIP_OVERLAP in the ws217 manifest only because its bbox touches the deck mass; brought with its hangers so
# they don't hang on nothing). Not taken: KY lintel soffit / walk fill, LA asphalt/walk (main has its own; SKIP_OVERLAP).
import bpy, json, bmesh
from collections import Counter
from mathutils.bvhtree import BVHTree
MS='/workspace/nj-scenes/montclair-state/'
NORTH=MS+'north/montclair_north.blend'
cand=json.load(open(MS+'scripts/ws238/m2c_candidates238.json'))
want=[n for n,v in cand.items() if v['cols'] and v['cols'][0] in ('KX_rhd_entrance','KX2_rhd_walk','LA_college_ave_door','KY_rhd_drive') and not v['hidden'] and v['region']=='M3b']
want=[n for n in want if not n.startswith('KX2_rhd_walk')]
want+=['KY_rhd_clearance_bar (photo: dark bar; text not modelled)']
want=[n for n in want if n not in bpy.data.objects]
print('M2C239 want',len(want),flush=True)
sc=bpy.context.scene
def coll(name,parent):
    c=bpy.data.collections.get(name) or bpy.data.collections.new(name)
    if c.name not in [x.name for x in parent.children]: parent.children.link(c)
    return c
NM=coll('NORTH_MERGE',sc.collection); ND=coll('N_site_detail_rhd',NM)
before=set(bpy.data.objects); libs0=set(l.filepath for l in bpy.data.libraries)
with bpy.data.libraries.load(NORTH,link=False) as (src,dst):
    have=set(src.objects); dst.objects=[n for n in want if n in have]
app=[o for o in dst.objects if o]
print('M2C239 appended',len(app),'of',len(want),'missing',[n for n in want if n not in have],flush=True)
for o in app:
    for c in list(o.users_collection): c.objects.unlink(o)
    ND.objects.link(o)
new=[o for o in bpy.data.objects if o not in before]
extra=[o for o in new if not o.users_collection]
for o in extra: ND.objects.link(o)
uh=[o.name for o in new if o.name.startswith(('UH','University Hall'))]
if uh: raise SystemExit('M2C239 University Hall object pulled in '+str(uh))
badl=[l.filepath for l in bpy.data.libraries if l.filepath not in libs0]
print('M2C239 new libs',badl,'types',Counter(o.type for o in new),'extra',[o.name[:30] for o in extra],flush=True)
for o in app: print('M2C239 obj',o.name[:60],'hr',o.hide_render,'mats',[m.name[:24] for m in o.data.materials],flush=True)
print('M2C239 new mats',[m.name for m in bpy.data.materials if m.users and not m.library and any(m.name in [s.name for s in o.data.materials] for o in app)][:30],flush=True)
# overlap report vs nearby main meshes (base mesh BVH intersect)
def bvh(o):
    bm=bmesh.new(); bm.from_mesh(o.data); bm.transform(o.matrix_world); t=BVHTree.FromBMesh(bm); bm.free(); return t
near=[bpy.data.objects[n] for n in bpy.data.objects.keys() if (n.startswith(('bx','bx2','KZ_','Red Hawk','KX_drive','LH_','LI_','LJ_','WS215','WS72_Kasser'))) and bpy.data.objects[n] not in new and bpy.data.objects[n].type=='MESH']
NB=[(o.name,bvh(o)) for o in near]
for o in app:
    t=bvh(o); hits=[n[:30] for n,b in NB if t.overlap(b)]
    print('M2C239 overlap',o.name[:40],hits,flush=True)
json.dump(sorted(o.name for o in new),open(MS+'scripts/ws239/m2c_new239.json','w'),indent=0)
for L in list(bpy.data.libraries):
    if L.filepath.endswith('north/montclair_north.blend') and L.filepath not in libs0:
        users=[(t,i.name) for t in ('objects','meshes','materials','images','node_groups','collections','textures','fonts','curves') for i in getattr(bpy.data,t) if i.library==L]
        print('M2C239 north-lib users',len(users),users[:10],flush=True)
        if not users: bpy.data.libraries.remove(L); print('M2C239 north lib removed',flush=True)
