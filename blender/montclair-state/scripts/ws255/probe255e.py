import sys; sys.stdout.reconfigure(line_buffering=True)
import bpy, os
F='/workspace/nj-scenes/montclair-state/montclair_state_ws255d.blend'
with bpy.data.libraries.load(F) as (a,b): b.objects=['Terrain_LiDAR_DTM_1m','WS250_W63_lawn_LiDAR2023_ground_patch_1m']
for o in b.objects:
    print('P255E',o.name,'mats',[m.name for m in o.data.materials if m],'uv',[u.name for u in o.data.uv_layers],'attrs',[a.name for a in o.data.attributes][:20],'mods',[(m.name,m.type, m.node_group.name if m.type=='NODES' and m.node_group else '') for m in o.modifiers],'hide_render',o.hide_render)
os._exit(0)
