# ws250 read-only: evaluated Terrain faces in the W63 box: area map (max face area per 4 m cell) + big faces list
import bpy, os, numpy as np
from mathutils import Vector
F='/workspace/nj-scenes/montclair-state/'+os.environ.get('F','montclair_state_ws250a.blend')
with bpy.data.libraries.load(F) as (a,b): b.objects=['Terrain_LiDAR_DTM_1m']
T=b.objects[0]; bpy.context.scene.collection.objects.link(T)
dg=bpy.context.evaluated_depsgraph_get(); me=T.evaluated_get(dg).to_mesh(); M=T.matrix_world
box=(-200,-138,138,218); A={}
big=[]
for p in me.polygons:
    c=M@p.center
    if not (box[0]<c.x<box[1] and box[2]<c.y<box[3]): continue
    k=(int((c.x-box[0])//4),int((c.y-box[2])//4)); A[k]=max(A.get(k,0),p.area)
    if p.area>3: big.append((p.area,round(c.x,1),round(c.y,1),len(p.vertices)))
print('FA250 cols x from',box[0],'step 4')
for j in range(19,-1,-1):
    print('FA250 y%4d '%(box[2]+4*j)+''.join('%5.1f'%A[(i,j)] if (i,j) in A else '   . ' for i in range(16)),flush=True)
big.sort(reverse=True); print('FA250 big',len(big),big[:25],flush=True)
os._exit(0)
