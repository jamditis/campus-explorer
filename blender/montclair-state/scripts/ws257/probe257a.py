# ws257 read-only: Feliciano E paving objects (ws252-ws256) - bbox, mats, verts, do they already carry joints?
import bpy, os, numpy as np
import sys; sys.stdout.reconfigure(line_buffering=True)
MS='/workspace/nj-scenes/montclair-state/'
with bpy.data.libraries.load(MS+'montclair_state.blend') as (a,b):
    b.objects=[n for n in a.objects if n.startswith(('WS252','WS253','WS254','WS255','WS256'))]
    mats=[m for m in a.materials if 'joint' in m.lower() or 'concrete' in m.lower()]
print('P257 joint/concrete mats in main:',mats)
for o in b.objects:
    if o.type!='MESH': print('P257',o.name,o.type); continue
    M=o.matrix_world; co=np.array([M@v.co for v in o.data.vertices])
    print('P257 %-70s v%6d f%6d x %.1f..%.1f y %.1f..%.1f z %.2f..%.2f mats %s mods %s'%(o.name[:70],len(o.data.vertices),len(o.data.polygons),co[:,0].min(),co[:,0].max(),co[:,1].min(),co[:,1].max(),co[:,2].min(),co[:,2].max(),[m.name for m in o.data.materials if m],[m.type for m in o.modifiers]))
os._exit(0)
