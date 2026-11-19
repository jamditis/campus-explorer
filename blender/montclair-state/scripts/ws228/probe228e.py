import bpy,bmesh,sys,os
import numpy as np
A=np.load('/workspace/nj-scenes/montclair-state/data/dtm_1m.npy')
def d(x,y): return float(A[min(499,max(0,int(y+250))),min(499,max(0,int(x+250)))])
o=bpy.data.objects['WS60_terrain_edge_apron_LiDAR_to_skirt']; t=bpy.data.objects['Terrain_LiDAR_DTM_1m']
av=sorted([v.co for v in o.data.vertices if -251<v.co.y<-247 and 140<v.co.x<247],key=lambda c:c.x)
print('P228E apron S verts',[(round(c.x,1),round(c.y,2),round(c.z-d(c.x,c.y),2)) for c in av][:40],flush=True)
tv=sorted([v.co for v in t.data.vertices if -249.5<v.co.y<-248 and 140<v.co.x<247],key=lambda c:c.x)
print('P228E terrain S verts',[(round(c.x,1),round(c.y,2),round(c.z-d(c.x,c.y),2)) for c in tv][::4][:40],flush=True)
sys.stdout.flush(); os._exit(0)
