import bpy
P='/workspace/nj-scenes/montclair-state/scripts/ws76/ws76_paint.blend'
for o in [o for o in bpy.data.objects if o.name.startswith('WS76_')]: bpy.data.objects.remove(o,do_unlink=True)
with bpy.data.libraries.load(P,link=False) as (fr,to): to.objects=[n for n in fr.objects if n.startswith('WS76_')]
for o in to.objects:
    if o: bpy.context.scene.collection.objects.link(o); o.use_fake_user=False
print('WS76 appended',[o.name for o in to.objects if o],flush=True)
