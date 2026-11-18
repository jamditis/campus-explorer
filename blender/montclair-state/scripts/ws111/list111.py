import bpy
M='/workspace/nj-scenes/montclair-state/montclair_state.blend'
with bpy.data.libraries.load(M) as (src,dst):
    names=list(src.objects); cols=list(src.collections)
import re
for n in names:
    if re.search(r'WS110|WS102|NA85|NA84|232846679|WS103|WS30|Terrain_LiDAR|WS104',n): print('L111',n)
for c in cols:
    if re.search(r'WS110|WS102|WS103|WS104',c): print('C111',c)
print('L111 total',len(names))
