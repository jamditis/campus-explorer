import bpy,bmesh,json,os
F=json.load(open('/workspace/nj-scenes/montclair-state/scripts/ws94/filler94.json'))
src=bpy.data.objects['WS76_accessible_lot_asphalt_ortho2020_UNVERIFIED_edges']
me=bpy.data.meshes.new('WS94_lot_slit_filler_asphalt')
bm=bmesh.new()
for ring in F:
    vs=[bm.verts.new(p) for p in ring]
    try: bm.faces.new(vs)
    except Exception as e: print("skip",e)
bmesh.ops.triangulate(bm,faces=bm.faces[:],quad_method='BEAUTY',ngon_method='EAR_CLIP')
for f in bm.faces:
    if f.normal.z<0: f.normal_flip()
bm.to_mesh(me); bm.free()
me.materials.append(src.data.materials[0] if src.data.materials else None)
ob=bpy.data.objects.new('WS94_lot_slit_filler_asphalt_UNVERIFIED',me)
for c in src.users_collection: c.objects.link(ob)
for p in me.polygons: p.use_smooth=False
print("P94 faces",len(me.polygons),"mat",me.materials[0] and me.materials[0].name)
if os.environ.get('SAVE')=='1':
    bpy.ops.wm.save_mainfile(); print("P94 SAVED")
