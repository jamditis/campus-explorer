import bpy
for o in list(bpy.data.objects): bpy.data.objects.remove(o)
with bpy.data.libraries.load('/workspace/nj-scenes/montclair-state/montclair_state.blend',link=False) as (a,b):
    b.objects=[n for n in a.objects if n.startswith('OQ_skirt_win_Calcia')]
for o in b.objects:
    bpy.context.scene.collection.objects.link(o); o['kit_note']='oq: lower-storey punched window (brown 3x3 lites, stucco surround, cast sill); UNVERIFIED style'
    print('KIT',o.name,len(o.data.polygons))
bpy.ops.wm.save_as_mainfile(filepath='/workspace/nj-scenes/assets/skirt_punched_window_kit_oq.blend',compress=True)
