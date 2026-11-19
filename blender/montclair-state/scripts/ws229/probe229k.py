import bpy,sys,numpy as np
A=np.load('/workspace/nj-scenes/montclair-state/data/dtm_1m.npy')
def d(x,y): return float(A[min(499,max(0,int(y+250))),min(499,max(0,int(x+250)))])
ap=bpy.data.objects['WS60_terrain_edge_apron_LiDAR_to_skirt']; me=ap.data; W=ap.matrix_world
n=0
for p in me.polygons:
    c=W@p.center
    if c.x>238 and c.y>-6 and c.y<260:
        vs=[W@me.vertices[i].co for i in p.vertices]; n+=1
        if n<=40: print('P229K f',p.index,round(p.area),[(round(v.x,1),round(v.y,1),round(v.z-d(v.x,v.y),2)) for v in vs],flush=True)
print('P229K n',n,flush=True)
sys.stdout.flush(); import os; os._exit(0)
