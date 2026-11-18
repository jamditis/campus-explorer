import bpy
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws60/edge_probe.py').read().split('xs=[v.co.x')[0])
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws60/apron.py').read())
ob=bpy.data.objects['WS60_terrain_edge_apron_LiDAR_to_skirt']
# check: max step between terrain edge and apron inner row, and apron outer vs skirt
import numpy as np
zs=np.array([v.co.z for v in ob.data.vertices]); print('AP60 z range',round(zs.min(),1),round(zs.max(),1))
for o in list(bpy.data.objects):
    if o!=ob: bpy.data.objects.remove(o)
bpy.ops.wm.save_as_mainfile(filepath='/workspace/nj-scenes/montclair-state/data/ws60/apron.blend'); print('AP60 saved data blend')
