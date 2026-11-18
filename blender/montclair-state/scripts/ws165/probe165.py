import bpy, os
M='/workspace/nj-scenes/montclair-state/montclair_state.blend'
want=lambda n: n.startswith(('WS110_ground','WS163_','WS164_')) or n in ('T_RedMaple_L1_0004',)
with bpy.data.libraries.load(M) as (s,d): d.objects=[n for n in s.objects if want(n)]
for o in d.objects:
    if o: bpy.context.scene.collection.objects.link(o)
print('LOADED',len(d.objects),flush=True)
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws165/fix165.py').read())
if os.environ.get('SAVE'): bpy.ops.wm.save_as_mainfile(filepath=os.environ['SAVE'])
