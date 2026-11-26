# ws249 pass 7 (CHAIN on ws249f): apply k249.json: 155 ws248 patch vertices on the berm toe SE of the east stand sunk
# 4 cm under the dense LiDAR-snapped terrain (max 0.47 m), so the terrain shows there and the toe crease goes away.
import bpy, json
TAG='F249G'; P=bpy.data.objects['WS248_E_stand_LiDAR2023_ground_patch_1m']
if not P.get('ws249g'):
    K=json.load(open('/workspace/nj-scenes/montclair-state/scripts/ws249/k249.json')); Mi=P.matrix_world.inverted(); M=P.matrix_world
    for i,z in K.items():
        v=P.data.vertices[int(i)]; w=M@v.co; w.z=z; v.co=Mi@w
    P.data.update(); P['ws249g']=1; print(TAG,'moved',len(K),flush=True)
