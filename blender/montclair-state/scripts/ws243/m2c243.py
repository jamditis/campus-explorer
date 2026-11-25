# ws243 ONE-SCENE M2 batch (c), slice 5: soccer stands + pitch as ONE unit (fr / fs pitch / fse / fst / ft fence+lights / fu).
# Same main-design overlap check as m2c242, except: PK_/PZ_ Feliciano DTM fills/feathers count as GROUND (synthetic terrain,
# not design); guessed PO_*_UNVERIFIED gutters are soft (reported); a main tree whose trunk (origin) stands inside a stand/pitch
# footprint (bbox shrunk 1 m) is removed (trees don't grow through bleachers/turf), canopy overhang elsewhere is allowed.
# Any other main mesh hit = hard conflict: the north object is dropped; if a stand's core (under_pad/understructure/risers/seating)
# is dropped, that whole stand group goes (no floating parts). Then PK fill verts under the kept footprints are pushed below them.
import bpy, json, bmesh, os, re
from mathutils import Vector
from mathutils.bvhtree import BVHTree
MS='/workspace/nj-scenes/montclair-state/'
NORTH=MS+'north/montclair_north.blend'
nxt=json.load(open(MS+'scripts/ws242/m2c_next242.json'))
G=['North_SoccerStands_fr','North_Pitch_fs','North_SoccerStandsEast_fs','North_SoccerStandsSouth_ft','North_PitchFence_ft','North_PitchLights_ft','North_PitchNorth_fu']
want=[n for n,v in nxt.items() if v['cols'] and v['cols'][0] in G and n not in bpy.data.objects]
print('M2C243 want',len(want),want,flush=True)
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
print('M2C243 appended',len(app),'missing',[n for n in want if n not in have],flush=True)
for o in app:
    c=coll('N_site_detail_soccer_stands' if 'Stands' in nxt[o.name]['cols'][0] else 'N_site_detail_pitch',NM)
    for x in list(o.users_collection): x.objects.unlink(o)
    c.objects.link(o)
new=[o for o in bpy.data.objects if o not in before]
for o in list(new):
    b=re.sub(r'\.\d{3}$','',o.name)
    if b!=o.name and b in bpy.data.objects and bpy.data.objects[b] not in new:
        o.user_remap(bpy.data.objects[b]); new.remove(o); bpy.data.objects.remove(o)
for o in new:
    if not o.users_collection: coll('N_site_detail_misc',NM).objects.link(o)
uh=[o.name for o in new if 'University Hall' in o.name or o.name.startswith('UH')]
if uh: raise SystemExit('M2C243 University Hall object pulled in '+str(uh))
bpy.context.view_layer.update()
def wbb(o):
    cs=[o.matrix_world@Vector(c) for c in o.bound_box]
    return [min(c[i] for c in cs) for i in range(3)],[max(c[i] for c in cs) for i in range(3)]
def bvh(o):
    bm=bmesh.new(); bm.from_mesh(o.data); bm.transform(o.matrix_world); t=BVHTree.FromBMesh(bm); bm.free(); return t
GROUND=('WS68_RHD_ground','Terrain','M3b','M3a','Context_skirt','WS60_terrain','Roads_OSM','Footpaths_OSM','BD_farfield','Grass','grass','PK_','PZ_')
mains=[o for o in bpy.data.objects if o.type=='MESH' and o not in new and not o.library and o.data and len(o.data.polygons)]
MB={o.name:wbb(o) for o in mains}
drop=[]; rep={}; trees=set()
for o in [x for x in new if x.type=='MESH']:
    lo,hi=wbb(o); t=bvh(o); hits=[]
    for m in mains:
        a,b=MB[m.name]
        if any(b[i]<lo[i]-0.05 or a[i]>hi[i]+0.05 for i in range(3)): continue
        if t.overlap(bvh(m)): hits.append(m.name)
    hard=[];soft=[]
    for h in hits:
        if h.startswith(GROUND) or 'terrain' in h.lower() or 'lawn' in h.lower(): continue
        if h.startswith('PO_') and 'UNVERIFIED' in h: soft.append(h); continue
        if h.startswith('T_'):
            p=bpy.data.objects[h].matrix_world.translation
            if lo[0]+1<p.x<hi[0]-1 and lo[1]+1<p.y<hi[1]-1: trees.add(h)
            else: soft.append(h)
            continue
        hard.append(h)
    rep[o.name]={'bbox':[[round(v,2) for v in lo],[round(v,2) for v in hi]],'hits':hits[:20],'hard':hard,'soft':soft}
    print('M2C243 chk',o.name[:44],'bb',[round(v,1) for v in lo],[round(v,1) for v in hi],'HARD' if hard else 'ok',[c[:30] for c in hard[:6]],'soft',[c[:24] for c in soft[:4]],flush=True)
    if hard: drop.append(o.name)
CORE=('stand_under_pad','stand_understructure','stand_risers','stand_seating')
pref={n.split('_')[0] for n in drop if n.endswith(CORE)}
for o in new:
    if o.type=='MESH' and o.name.split('_')[0] in pref and o.name not in drop: drop.append(o.name)
# dependants of a dropped front walkway: its entry steps
for n in list(drop):
    if n.endswith('front_walkway'):
        s=n.split('_')[0]+'_stand_entry_steps'
        if s in bpy.data.objects and s not in drop: drop.append(s)
for n in drop: bpy.data.objects.remove(bpy.data.objects[n])
for n in trees:
    if n in bpy.data.objects: bpy.data.objects.remove(bpy.data.objects[n])
_OFF[:]=[(a,b) for a,b in _OFF if a in bpy.data.objects]
kept=sorted(o.name for o in new if o.name in bpy.data.objects)
print('M2C243 dropped',len(drop),drop,'trees removed',sorted(trees),flush=True)
# push PK fill (plain DTM-fill mesh) under the kept footprints: any PK vert under a kept up-facing surface -> that surface - 0.05
KB=[bvh(bpy.data.objects[n]) for n in kept if bpy.data.objects[n].type=='MESH']
pk=0
for po in [o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith('PK_')]:
    M=po.matrix_world; Mi=M.inverted()
    for v in po.data.vertices:
        w=M@v.co; best=None
        for t in KB:
            h=t.ray_cast(Vector((w.x,w.y,w.z+30)),Vector((0,0,-1)),60)[0]
            if h is not None and h.z>w.z-3 and (best is None or h.z<best): best=h.z
        if best is not None and w.z>best-0.05:
            w.z=best-0.05; v.co=Mi@w; pk+=1
    po.data.update()
print('M2C243 PK verts pushed under',pk,flush=True)
json.dump({'kept':kept,'dropped':drop,'trees_removed':sorted(trees),'pk_pushed':pk,'report':rep},open(MS+'scripts/ws243/m2c_new243.json','w'),indent=0)
for L in list(bpy.data.libraries):
    if L.filepath.endswith('north/montclair_north.blend') and L.filepath not in libs0:
        users=[i for t in ('objects','meshes','materials','images','node_groups','collections') for i in getattr(bpy.data,t) if i.library==L]
        if not users: bpy.data.libraries.remove(L)
print('M2C243 kept',len(kept),flush=True)
