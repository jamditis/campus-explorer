# ws256c (M2c review item ge_police_south_walk -> MERGED): the north file's concrete walk around the police terrace
# (S / E / W sides + the strip along the building's S face) was never merged (ws254: inconclusive, main base terrain has
# no faces there). probe256d with the north-merged ground loaded: walk vs main ground p50 0.00 (p5 -0.42, p95 +0.22).
# Merge: append from north, delete the 106 faces under main's terrace walls / Red Hawk W core / deck / police foundation,
# drape every vertex to main's evaluated ground (5-sample mean, r 0.35 m) + 3 cm (police_walk256.json from probe256d).
# Walk layout from the north file (OSM-based); finish/width UNVERIFIED.
import bpy, bmesh, json
TAG='F256C'; MS='/workspace/nj-scenes/montclair-state/'
J=json.load(open(MS+'scripts/ws256/police_walk256.json'))
if 'ge_police_south_walk' in bpy.data.objects: raise SystemExit('already in main')
with bpy.data.libraries.load(MS+'north/montclair_north.blend') as (a,b): b.objects=['ge_police_south_walk']
o=b.objects[0]
col=bpy.data.objects['ge_police_terrace_walls'].users_collection[0]; col.objects.link(o)
# reuse main's material if the same name already exists
for i,m in enumerate(o.data.materials):
    if m and m.name.endswith(('.001','.002')) and m.name.rsplit('.',1)[0] in bpy.data.materials:
        o.data.materials[i]=bpy.data.materials[m.name.rsplit('.',1)[0]]; print(TAG,'mat remap',m.name,flush=True)
print(TAG,'mats',[m.name for m in o.data.materials if m],'col',col.name,flush=True)
me=o.data; Mi=o.matrix_world.inverted(); M=o.matrix_world
mv=[0,0]
for k,t in J['tgt'].items():
    v=me.vertices[int(k)]; w=M@v.co; d=t-w.z; mv[0]=min(mv[0],d); mv[1]=max(mv[1],d); w.z=t; v.co=Mi@w
bm=bmesh.new(); bm.from_mesh(me); bm.faces.ensure_lookup_table()
dl=set(J['del']); bmesh.ops.delete(bm,geom=[bm.faces[i] for i in dl],context='FACES')
loose=[v for v in bm.verts if not v.link_faces]; bmesh.ops.delete(bm,geom=loose,context='VERTS')
bm.to_mesh(me); bm.free(); me.update()
print(TAG,'merged',o.name,'verts',len(me.vertices),'faces',len(me.polygons),'drape d %.2f..%.2f'%tuple(mv),'deleted faces',len(dl),flush=True)
