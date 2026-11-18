# ws218 ONE-SCENE M2 batch (a): append University Hall (UH*), Children's Center and OF/OFD objects from north/montclair_north.blend
# into main under NORTH_MERGE/N_buildings, using the ws217 manifest (APPEND class only). Local north objects are appended
# (link=False); north objects that are themselves linked from assets/windows_*.blend / njt_trains.blend are LINKED from that
# asset file (as main does). Objects whose library is //../montclair_state.blend or //sprague_cafe_src.blend are never listed
# as local in north, and the asset search below excludes those files, so they can never be appended back.
import bpy, json, os
from collections import Counter
MS='/workspace/nj-scenes/montclair-state/'
NORTH=MS+'north/montclair_north.blend'
man=json.load(open(MS+'scripts/ws217/north_manifest217.json'))
HID=set(json.load(open(MS+'scripts/ws218/north_hidden218.json')))  # hidden/replaced in north (probe218b): OSM block + its windows, parapet, window templates
want=[n for n,v in man.items() if (v[0] in ('APPEND','NONMESH_EMPTY') or n.startswith('UH ground-floor lobby glazing')) and (n.startswith(('UH','OF','University Hall')) or "Children" in n) and n not in HID]
want=[n for n in want if n not in bpy.data.objects]
print('M2A want',len(want),flush=True)
sc=bpy.context.scene
def coll(name,parent):
    c=bpy.data.collections.get(name) or bpy.data.collections.new(name)
    if c.name not in [x.name for x in parent.children]: parent.children.link(c)
    return c
NM=coll('NORTH_MERGE',sc.collection); NB=coll('N_buildings',NM)
IMG0=set(i.name for i in bpy.data.images)
before=set(bpy.data.objects); libs0=set(l.filepath for l in bpy.data.libraries)
with bpy.data.libraries.load(NORTH,link=False) as (src,dst):
    loc=set(src.objects); dst.objects=[n for n in want if n in loc]
app=[o for o in dst.objects if o]
miss=[n for n in want if n not in loc]
print('M2A appended',len(app),'linked-in-north',len(miss),flush=True)
linked=[]
if miss:
    A='/workspace/nj-scenes/assets/'
    for f in sorted(os.listdir(A)):
        if not (f.startswith('windows_') or f.startswith('njt_trains')) or not f.endswith('.blend'): continue
        rem=[n for n in miss if n not in [o.name for o in linked]]
        if not rem: break
        with bpy.data.libraries.load(A+f,link=True,relative=True) as (src,dst):
            have=set(src.objects); dst.objects=[n for n in rem if n in have]
        got=[o for o in dst.objects if o]; linked+=got
        if got: print('M2A linked',len(got),'from',f,flush=True)
    print('M2A still missing',[n for n in miss if n not in [o.name for o in linked]][:20],flush=True)
for o in app+linked:
    if not o.users_collection: NB.objects.link(o)
# parents/indirect objects pulled in by dependency: put them in the collection too (hidden empties fine)
extra=[o for o in bpy.data.objects if o not in before and not o.users_collection]
for o in extra: NB.objects.link(o)
libs=[l.filepath for l in bpy.data.libraries]
bad=[l for l in libs if l not in libs0 and ('montclair_state.blend' in l or 'sprague_cafe_src' in l)]
print('M2A new libs',[l for l in libs if l not in libs0],flush=True)
newsprague=[o.name for o in bpy.data.objects if o not in before and o.library and ('sprague_cafe_src' in o.library.filepath or 'montclair_state.blend' in o.library.filepath)]
if newsprague: raise SystemExit('M2A forbidden objects '+str(newsprague[:10]))
print('M2A extra',len(extra),'libs',libs,flush=True)
if bad: raise SystemExit('M2A forbidden library '+str(bad))
for o in NB.objects:
    if o.type=='EMPTY' and o.instance_collection: pass
print('M2A instcoll',Counter((o.instance_collection.name,bool(o.instance_collection.library)) for o in NB.objects if o.type=='EMPTY' and o.instance_collection).most_common(8),flush=True)
print('M2A types',Counter(o.type for o in NB.objects),'total in N_buildings',len(NB.objects),flush=True)
# drop the empty library entry the append leaves for the north file (any ID still using it is reported)
for L in list(bpy.data.libraries):
    if L.filepath.endswith('north/montclair_north.blend'):
        users=[(t,i.name) for t in ('objects','meshes','materials','images','node_groups','collections','textures','fonts','curves') for i in getattr(bpy.data,t) if i.library==L]
        print('M2A north-lib users',len(users),users[:10],flush=True)
        if not users: bpy.data.libraries.remove(L); print('M2A north lib removed',flush=True)
# image check: no ortho/raster pulled in with the batch
print('M2A images new', [i.name for i in bpy.data.images if not i.library and i.name not in IMG0][:30],flush=True)
for o in NB.objects:
    if 'gutters, white K-style' in o.name: print('M2A gutter',o.name,[(m.type,m.name) for m in o.modifiers],tuple(round(x,2) for x in o.location),o.parent,flush=True)
# north-file bug: the Children's Center gutter mesh has every vertex z doubled (226.7-229.2 vs eaves 113.55-114.75 m);
# halving z puts the gutter tops at 113.4-114.6 m, just under each eave line. Fix the mesh in main (north file untouched).
for o in NB.objects:
    if 'gutters, white K-style' in o.name and o.type=='MESH':
        zs=[v.co.z for v in o.data.vertices]
        if min(zs)>200:
            for v in o.data.vertices: v.co.z*=0.5
            print('M2A gutter z halved',round(min(zs)/2,2),round(max(zs)/2,2),flush=True)
