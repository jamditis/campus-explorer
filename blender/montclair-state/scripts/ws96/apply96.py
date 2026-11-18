import bpy,bmesh,json,os
G=json.load(open('/workspace/nj-scenes/montclair-state/scripts/ws96/gap96b.json'))
PROBE=os.environ.get('PROBE')=='1'
if PROBE:
    exec(open('/workspace/nj-scenes/montclair-state/scripts/ws95/lip95.py').read().split("sc.render.filepath")[0])
T=bpy.data.objects['Terrain_LiDAR_DTM_1m']; imw=T.matrix_world.inverted(); mw=T.matrix_world
n=0
for i,d in G['low']:
    v=T.data.vertices[i]; w=mw@v.co; w.z+=d; v.co=imw@w; n+=1
T.data.update(); print("A96 terrain lowered",n)
ref=bpy.data.objects['WS94_lot_slit_filler_asphalt_UNVERIFIED']
me=bpy.data.meshes.new('WS96_lot_E_edge_gap_filler_asphalt_UNVERIFIED')
bm=bmesh.new()
for ring in G['fill']:
    vs=[bm.verts.new(p) for p in ring]
    try:
        f=bm.faces.new(vs)
    except ValueError: continue
bmesh.ops.triangulate(bm,faces=bm.faces[:])
for f in bm.faces:
    f.normal_update()
    if f.normal.z<0: f.normal_flip()
bm.to_mesh(me); bm.free()
o=bpy.data.objects.new(me.name,me)
for m in ref.data.materials: me.materials.append(m)
(ref.users_collection[0] if not PROBE else bpy.context.scene.collection).objects.link(o)
print("A96 filler faces",len(me.polygons))
if PROBE:
    o.color=(1,0,1,1)
    for nm,c in (('after',None),):
        sc.render.filepath='/workspace/nj-scenes/montclair-state/scripts/ws96/lip_after.png'; bpy.ops.render.render(write_still=True); print("WROTE")
if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print("A96 SAVED")
