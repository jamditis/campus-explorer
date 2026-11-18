import bpy,os
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws72/lite_load.py').read())
KEEP=tuple(os.environ['KEEP'].split(','))
for o in list(bpy.data.objects):
    if not o.name.startswith(KEEP) or (o.name[-4:-3]=='.' and o.name[-3:].isdigit()):
        if 'DTM_target' not in o.name: bpy.data.objects.remove(o)
T0=bpy.data.objects['Terrain_LiDAR_DTM_1m']
for m in T0.modifiers:
    if m.name.startswith('WS64'): m.show_viewport=False
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws72/'+os.environ.get("WALK","walk72.py")+'').read())
if os.environ.get('LSAVE'): bpy.ops.wm.save_as_mainfile(filepath=os.environ['LSAVE'])
