import bpy
P='/workspace/nj-scenes/montclair-state/data/ws60/apron_uv.blend'
if 'WS60_terrain_edge_apron_LiDAR_to_skirt' in bpy.data.objects: print('A60 already'); raise SystemExit
t=bpy.data.objects['Terrain_LiDAR_DTM_1m']
with bpy.data.libraries.load(P,link=False) as (s,d): d.objects=['WS60_terrain_edge_apron_LiDAR_to_skirt']
for o in d.objects:
    for c in t.users_collection: c.objects.link(o)
    # reuse main's skirt materials, not the appended copies
    sk=bpy.data.objects['Context_skirt_3DEP_ortho_4km'].data.materials
    for i in range(len(o.data.materials)): o.data.materials[i]=sk[i]
bpy.ops.outliner.orphans_purge(do_recursive=True)
bpy.ops.wm.save_mainfile(); print('A60 saved')
