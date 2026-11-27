# ws257b (M2c review item "MSU Maintenance Building (OSM 232850495; BACKDROP massing, LiDAR...)" -> MERGED).
# OSM way 232850495 = building=university, name="Maintenance Building" (checked on the OSM API this session). Main had nothing
# there (x -391..-325, y -77..-39, W of the cogen plant / SW of Red Hawk Deck): probe257c/d found no main structure inside the
# massing (Red Hawk Deck, rhd retaining wall and the WS74 cogen lot asphalt all stay outside), no ground above its roof; it sits
# on the slope (ground up to 5 m above its base on the uphill side, as a bank-cut building would). 29 base verts that stood up to
# 8 cm over main's evaluated ground are candidates (maint257.json from probe257e); only the BOTTOM ring (z < base + 0.2) is
# lowered to ground - 15 cm; the 1 m plinth's top ring (116.37) stays (it stands up to 0.47 m clear of the ground = a visible plinth). Heights are the north file's
# LiDAR massing; finish/colours UNVERIFIED (backdrop detail level, no windows).
import bpy, json
TAG='F257B'; MS='/workspace/nj-scenes/montclair-state/'
J=json.load(open(MS+'scripts/ws257/maint257.json'))
N='MSU Maintenance Building (OSM 232850495; BACKDROP massing, LiDA'
if any(o.name.startswith(N) for o in bpy.data.objects): raise SystemExit('already in main')
with bpy.data.libraries.load(MS+'north/montclair_north.blend') as (a,b): b.objects=[n for n in a.objects if n.startswith(N)]
o=b.objects[0]
col=bpy.data.objects['fo_cogen_body'].users_collection[0]; col.objects.link(o)
for i,m in enumerate(o.data.materials):
    if m and m.name.endswith(('.001','.002')) and m.name.rsplit('.',1)[0] in bpy.data.materials:
        o.data.materials[i]=bpy.data.materials[m.name.rsplit('.',1)[0]]; print(TAG,'mat remap',m.name,flush=True)
print(TAG,'mats',[m.name for m in o.data.materials if m],'col',col.name,'mods',[m.type for m in o.modifiers],flush=True)
me=o.data; M=o.matrix_world; Mi=M.inverted(); dmin=0; nlow=0
zb=min((M@v.co).z for v in me.vertices)
for k,t in J['tgt'].items():
    v=me.vertices[int(k)]; w=M@v.co
    if w.z>zb+0.2: continue
    nlow+=1; dmin=min(dmin,t-w.z); w.z=min(w.z,t); v.co=Mi@w
me.update(); print(TAG,'merged',o.name,'verts',len(me.vertices),'bottom verts lowered',nlow,'max drop %.2f'%dmin,flush=True)
