import bpy
for n in ('WS75_sprague_lot_asphalt_ortho2020_UNVERIFIED_edges','WS80_sprague_lot_fill_asphalt_ortho2020_UNVERIFIED_edges'):
    me=bpy.data.objects[n].data; me.materials[0]=bpy.data.materials['fn_lot_asphalt']
dups=[m.name for m in bpy.data.materials if m.name.startswith('fn_lot_asphalt.')]
for d in dups:
    m=bpy.data.materials[d]; print('WS81G dup',d,m.users,flush=True)
    if m.users==0: bpy.data.materials.remove(m)
bpy.data.orphans_purge(do_local_ids=True,do_linked_ids=False,do_recursive=True)
print('WS81G mats',[bpy.data.objects[n].data.materials[0].name for n in ('WS75_sprague_lot_asphalt_ortho2020_UNVERIFIED_edges','WS80_sprague_lot_fill_asphalt_ortho2020_UNVERIFIED_edges')],'remaining dups',[m.name for m in bpy.data.materials if m.name.startswith('fn_lot_asphalt.')],flush=True)
bpy.ops.wm.save_mainfile(); print('WS81G SAVED',flush=True)
