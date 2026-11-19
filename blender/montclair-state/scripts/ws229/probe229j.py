# ws229 W53i: structure of the terrain east boundary + WS60 apron north of A2 (y > -33.5)
import bpy,sys,bmesh,collections,numpy as np
A=np.load('/workspace/nj-scenes/montclair-state/data/dtm_1m.npy')
def d(x,y): return float(A[min(499,max(0,int(y+250))),min(499,max(0,int(x+250)))])
t=bpy.data.objects['Terrain_LiDAR_DTM_1m']; bm=bmesh.new(); bm.from_mesh(t.data)
bv=[v for v in bm.verts if v.is_boundary and v.co.x>240 and v.co.y>-33.6]
print('P229J terrain boundary verts x>240,y>-33.6',len(bv),flush=True)
for v in sorted(bv,key=lambda v:v.co.y)[::max(1,len(bv)//25)]: print('P229J tb',round(v.co.x,2),round(v.co.y,2),'dz',round(v.co.z-d(v.co.x,v.co.y),2),'nf',len(v.link_faces),'maxarea',round(max(f.calc_area() for f in v.link_faces),1),flush=True)
ap=bpy.data.objects['WS60_terrain_edge_apron_LiDAR_to_skirt']; me=ap.data; W=ap.matrix_world
vs=[W@v.co for v in me.vertices if (W@v.co).y>-33.6 and (W@v.co).x>240]
print('P229J apron verts',len(vs),'xbuckets',sorted(collections.Counter(round(v.x) for v in vs).items())[:30],flush=True)
rows=collections.Counter(round(v.y,2) for v in vs); print('P229J apron rows',len(rows),'row sizes',collections.Counter(rows.values()),'y range',min(v.y for v in vs),max(v.y for v in vs),flush=True)
print('P229J apron total v/f',len(me.vertices),len(me.polygons),'mods',[m.name for m in ap.modifiers],flush=True)
sys.stdout.flush(); import os; os._exit(0)
