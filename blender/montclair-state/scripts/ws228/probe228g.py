import bpy,bmesh,sys,os
import numpy as np
A=np.load('/workspace/nj-scenes/montclair-state/data/dtm_1m.npy')
def dtm(x,y):
    gx=x+250-0.5; gy=y+250-0.5; i=int(np.floor(gy)); j=int(np.floor(gx)); fy=gy-i; fx=gx-j
    i=min(498,max(0,i)); j=min(498,max(0,j))
    return float(A[i,j]*(1-fx)*(1-fy)+A[i,j+1]*fx*(1-fy)+A[i+1,j]*(1-fx)*fy+A[i+1,j+1]*fx*fy)
t=bpy.data.objects['Terrain_LiDAR_DTM_1m']; bm=bmesh.new(); bm.from_mesh(t.data)
H=[]
for v in bm.verts:
    c=v.co
    if 140<=c.x<=247 and -250<=c.y<=-33:
        dz=c.z-dtm(c.x,c.y)
        if dz>0.5 and not v.link_faces: H.append((round(dz,2),round(c.x,1),round(c.y,1),v.is_boundary,round(max(f.calc_area() for f in v.link_faces),1) if v.link_faces else 0,len(v.link_faces)))
H.sort(reverse=True); print('P228G high verts',len(H),flush=True)
for h in H[:40]: print('P228G',h,flush=True)
sys.stdout.flush(); os._exit(0)
