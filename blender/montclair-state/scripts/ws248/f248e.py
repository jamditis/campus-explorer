# ws248 pass 4 (CHAIN on ws248d): drop patch faces where the dense snapped terrain already sits above them (k248e.json)
import bpy, bmesh, json
o=bpy.data.objects['WS248_E_stand_LiDAR2023_ground_patch_1m']; D=set(json.load(open('/workspace/nj-scenes/montclair-state/scripts/ws248/k248e.json')))
if not o.get('ws248e'):
    bm=bmesh.new(); bm.from_mesh(o.data); bm.faces.ensure_lookup_table()
    bmesh.ops.delete(bm,geom=[bm.faces[i] for i in D],context='FACES_ONLY'); bm.to_mesh(o.data); bm.free(); o['ws248e']=1
    # loose verts left by FACES_ONLY are harmless; drop them for tidiness
    bm=bmesh.new(); bm.from_mesh(o.data); lv=[v for v in bm.verts if not v.link_faces]; bmesh.ops.delete(bm,geom=lv,context='VERTS'); bm.to_mesh(o.data); bm.free()
print('F248E patch faces now',len(o.data.polygons),flush=True)
