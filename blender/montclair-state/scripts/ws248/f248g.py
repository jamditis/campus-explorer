# ws248g (CHAIN on ws248f2): apply k248g.json (patch vertices sunk 4 cm under the dense snapped terrain where it covers them)
import bpy, json
o=bpy.data.objects['WS248_E_stand_LiDAR2023_ground_patch_1m']; J=json.load(open('/workspace/nj-scenes/montclair-state/scripts/ws248/k248g.json'))
if not o.get('ws248g'):
    for k,z in J.items(): o.data.vertices[int(k)].co.z=z
    o.data.update(); o['ws248g']=1
print('F248G sunk',len(J),flush=True)
