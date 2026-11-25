# ws242 ONE-SCENE M2 batch (c), slice 4: clean groups from ws241/m2c_next241.json: North_terrain walks, pitch north (fu),
# soccer stands (fr/fs/ft clean parts), cogen shed (gl), Sprague field apron (go). Appended from north into NORTH_MERGE/N_site_detail_<tag>.
# Each object is checked against main's own design: BVH overlap vs every main mesh whose world bbox intersects it (terrain/skirt and
# generic context excluded from the conflict list but reported); an object that overlaps a main building/paving mesh is
# REMOVED again (not merged) and listed, so main's design wins.
import bpy, json, bmesh, os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
MS='/workspace/nj-scenes/montclair-state/'
NORTH=MS+'north/montclair_north.blend'
nxt=json.load(open(MS+'scripts/ws241/m2c_next241.json'))
G=os.environ.get('M2CG','North_terrain,North_PitchNorth_fu,North_SoccerStands_fr,North_SoccerStandsEast_fs,North_SoccerStandsSouth_ft,North_CogenShed_gl,North_SpragueField_apron_go').split(',')
want=[n for n,v in nxt.items() if v['cols'] and v['cols'][0] in G and v['status']=='clean' and n not in bpy.data.objects]
print('M2C242 want',len(want),flush=True)
print('M2C242 main has NJ Transit Deck', 'NJ Transit Deck' in bpy.data.objects, [n for n in bpy.data.objects.keys() if 'NJT' in n or 'Transit' in n][:10],flush=True)
sc=bpy.context.scene
def coll(name,parent):
    c=bpy.data.collections.get(name) or bpy.data.collections.new(name)
    if c.name not in [x.name for x in parent.children]: parent.children.link(c)
    return c
NM=coll('NORTH_MERGE',sc.collection)
before=set(bpy.data.objects); libs0=set(l.filepath for l in bpy.data.libraries)
with bpy.data.libraries.load(NORTH,link=False) as (src,dst):
    have=set(src.objects); dst.objects=[n for n in want if n in have]
app=[o for o in dst.objects if o]
print('M2C242 appended',len(app),'missing',[n for n in want if n not in have],flush=True)
tagof={'North_terrain':'terrain_walks','North_PitchNorth_fu':'pitch_north','North_SoccerStands_fr':'soccer_stands','North_SoccerStandsEast_fs':'soccer_stands','North_SoccerStandsSouth_ft':'soccer_stands','North_CogenShed_gl':'cogen_shed','North_SpragueField_apron_go':'sprague_field_apron'}
for o in app:
    c=coll('N_site_detail_'+tagof.get(nxt[o.name]['cols'][0],'misc'),NM)
    for x in list(o.users_collection): x.objects.unlink(o)
    c.objects.link(o)
new=[o for o in bpy.data.objects if o not in before]
# instance sources (grass clumps) duplicated by the append: remap to main's existing copies, then remove the duplicates
import re
for o in list(new):
    b=re.sub(r'\.\d{3}$','',o.name)
    if b!=o.name and b in bpy.data.objects and bpy.data.objects[b] not in new:
        o.user_remap(bpy.data.objects[b]); print('M2C242 remap',o.name,'->',b,flush=True)
        new.remove(o); bpy.data.objects.remove(o)
for o in new:
    if not o.users_collection: coll('N_site_detail_misc',NM).objects.link(o)
uh=[o.name for o in new if 'University Hall' in o.name or o.name.startswith('UH')]
if uh: raise SystemExit('M2C242 University Hall object pulled in '+str(uh))
bpy.context.view_layer.update()
def wbb(o):
    cs=[o.matrix_world@Vector(c) for c in o.bound_box]
    return [min(c[i] for c in cs) for i in range(3)],[max(c[i] for c in cs) for i in range(3)]
def bvh(o):
    bm=bmesh.new(); bm.from_mesh(o.data); bm.transform(o.matrix_world); t=BVHTree.FromBMesh(bm); bm.free(); return t
GROUND=('WS68_RHD_ground','Terrain','M3b','M3a','Context_skirt','WS60_terrain','Roads_OSM','Footpaths_OSM','BD_farfield','Grass','grass')
mains=[o for o in bpy.data.objects if o.type=='MESH' and o not in new and not o.library and o.data and len(o.data.polygons)]
MB={o.name:wbb(o) for o in mains}
drop=[]; rep={}
for o in [x for x in new if x.type=='MESH']:
    lo,hi=wbb(o); t=bvh(o); hits=[]
    for m in mains:
        a,b=MB[m.name]
        if any(b[i]<lo[i]-0.05 or a[i]>hi[i]+0.05 for i in range(3)): continue
        if t.overlap(bvh(m)): hits.append(m.name)
    conf=[h for h in hits if not h.startswith(GROUND) and 'terrain' not in h.lower() and 'lawn' not in h.lower()]
    rep[o.name]={'bbox':[[round(v,2) for v in lo],[round(v,2) for v in hi]],'hits':hits[:20],'conflict':conf[:20]}
    print('M2C242 chk',o.name[:50],'bb',[round(v,1) for v in lo],[round(v,1) for v in hi],'hits',[h[:28] for h in hits[:8]],'CONFLICT' if conf else 'ok',[c[:28] for c in conf[:6]],flush=True)
    if conf: drop.append(o.name)
# conflicts with main's own design -> keep main, drop the north object (whole group kept consistent by the report)
kept=sorted(o.name for o in new if o.name not in drop)
for n in drop:
    o=bpy.data.objects[n]; bpy.data.objects.remove(o)
print('M2C242 dropped',len(drop),drop,flush=True)
json.dump({'kept':kept,'dropped':drop,'report':rep},open(MS+'scripts/ws242/m2c_new242.json','w'),indent=0)
for L in list(bpy.data.libraries):
    if L.filepath.endswith('north/montclair_north.blend') and L.filepath not in libs0:
        users=[(t,i.name) for t in ('objects','meshes','materials','images','node_groups','collections','textures','fonts','curves') for i in getattr(bpy.data,t) if i.library==L]
        if not users: bpy.data.libraries.remove(L); print('M2C242 north lib removed',flush=True)
        else: print('M2C242 north-lib users',len(users),users[:8],flush=True)
print('M2C242 kept',len(kept),flush=True)
