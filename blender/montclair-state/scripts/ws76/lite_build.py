import bpy,os
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws72/lite_load.py').read())
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws73/crop.py').read())
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws76/apply76b.py').read())
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws76/apply76a.py').read())
objs={o for o in bpy.data.objects if o.name.startswith('WS76_')}
bpy.data.libraries.write('/workspace/nj-scenes/montclair-state/scripts/ws76/ws76_paint.blend',objs,fake_user=True)
print('WS76 wrote paint blend',[o.name for o in objs],flush=True)
