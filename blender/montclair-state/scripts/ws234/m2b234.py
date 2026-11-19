# ws234 ONE-SCENE M2 batch (b): Montclair State University station (NJ Transit Montclair-Boonton Line) platform/canopy/stairs,
# Montclair Heights station kit (MH), Montclair Line ballast/rails/catenary, and the two NJT consists (instancer empties of the
# njt_trains.blend asset collections) from north/montclair_north.blend into main under NORTH_MERGE/N_station_rail.
# Same rules as m2a218b: manifest APPEND/NONMESH only; objects hidden in north (probe234a: 16 superseded backups/placeholders)
# are NOT appended; north objects linked from assets/njt_trains.blend are LINKED from that asset (no copies); objects whose
# library is //../montclair_state.blend or //sprague_cafe_src.blend can never come in. NJT_path_trackB (hidden path curve for
# consist B's follow-path) comes in hidden so the constraint keeps its target. University Hall untouched.
import bpy, json, os
from collections import Counter
MS='/workspace/nj-scenes/montclair-state/'
NORTH=MS+'north/montclair_north.blend'
vis=json.load(open(MS+'scripts/ws234/m2b_vis234.json'))
want=[n for n,v in vis.items() if isinstance(v,dict) and (v['vis'] or n=='NJT_path_trackB')]
want=[n for n in want if n not in bpy.data.objects]
print('M2B want',len(want),flush=True)
sc=bpy.context.scene
def coll(name,parent):
    c=bpy.data.collections.get(name) or bpy.data.collections.new(name)
    if c.name not in [x.name for x in parent.children]: parent.children.link(c)
    return c
NM=coll('NORTH_MERGE',sc.collection); NS=coll('N_station_rail',NM)
IMG0=set(i.name for i in bpy.data.images)
before=set(bpy.data.objects); libs0=set(l.filepath for l in bpy.data.libraries)
loc_want=[n for n in want if not vis[n]['lib']]
lnk_want=[n for n in want if vis[n]['lib']]
with bpy.data.libraries.load(NORTH,link=False) as (src,dst):
    have=set(src.objects); dst.objects=[n for n in loc_want if n in have]
app=[o for o in dst.objects if o]
print('M2B appended',len(app),'of',len(loc_want),flush=True)
linked=[]
if lnk_want:
    with bpy.data.libraries.load('/workspace/nj-scenes/assets/njt_trains.blend',link=True,relative=True) as (src,dst):
        have=set(src.objects); dst.objects=[n for n in lnk_want if n in have]
    linked=[o for o in dst.objects if o]
    print('M2B linked',len(linked),'of',len(lnk_want),'missing',[n for n in lnk_want if n not in [o.name for o in linked]],flush=True)
for o in app+linked:
    if not o.users_collection: NS.objects.link(o)
extra=[o for o in bpy.data.objects if o not in before and not o.users_collection]
for o in extra: NS.objects.link(o)
print('M2B extra',len(extra),[o.name[:40] for o in extra][:10],flush=True)
p=bpy.data.objects.get('NJT_path_trackB')
if p and p in app: p.hide_render=True; p.hide_viewport=True
new=[o for o in bpy.data.objects if o not in before]
bad=[o.name for o in new if o.library and ('sprague_cafe_src' in o.library.filepath or 'montclair_state.blend' in o.library.filepath)]
if bad: raise SystemExit('M2B forbidden objects '+str(bad[:10]))
badl=[l.filepath for l in bpy.data.libraries if l.filepath not in libs0 and ('montclair_state.blend' in l.filepath or 'sprague_cafe_src' in l.filepath)]
if badl: raise SystemExit('M2B forbidden library '+str(badl))
uh=[o.name for o in new if o.name.startswith(('UH','University Hall'))]
if uh: raise SystemExit('M2B University Hall object pulled in '+str(uh[:5]))
print('M2B new libs',[l.filepath for l in bpy.data.libraries if l.filepath not in libs0],flush=True)
print('M2B instcoll',Counter((o.instance_collection.name,bool(o.instance_collection.library)) for o in new if o.type=='EMPTY' and o.instance_collection),flush=True)
print('M2B types',Counter(o.type for o in new),'N_station_rail',len(NS.objects),'new total',len(new),flush=True)
print('M2B constraints',Counter((c.type, c.target.name if getattr(c,'target',None) else None) for o in new for c in o.constraints),flush=True)
for L in list(bpy.data.libraries):
    if L.filepath.endswith('north/montclair_north.blend'):
        users=[(t,i.name) for t in ('objects','meshes','materials','images','node_groups','collections','textures','fonts','curves') for i in getattr(bpy.data,t) if i.library==L]
        print('M2B north-lib users',len(users),users[:10],flush=True)
        if not users: bpy.data.libraries.remove(L); print('M2B north lib removed',flush=True)
print('M2B images new',[(i.name,i.size[:]) for i in bpy.data.images if not i.library and i.name not in IMG0][:30],flush=True)
json.dump(sorted(o.name for o in new),open(MS+'scripts/ws234/m2b_new234.json','w'),indent=0)
