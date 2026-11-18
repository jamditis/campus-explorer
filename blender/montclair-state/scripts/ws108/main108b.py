import bpy
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws108/winfix108.py').read())
o=bpy.data.objects.get('WS105_PanzerE_side_lower_walkway_concrete_LiDAR2023_ortho2020_U')
if o: o.name='WS105_PanzerE_lower_walkway_concrete_LiDAR2023_ortho2020_UNVERIFIED'; print('REN108b',o.name)
bpy.ops.wm.save_mainfile(); print('M108b SAVED',flush=True)
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws105/cut105.py').read().replace('ws105/render_cut105','ws108/render_cut108'))
