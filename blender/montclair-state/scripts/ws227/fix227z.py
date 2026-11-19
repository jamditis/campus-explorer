# W53c root cause (probe227b): the residual high ground in the SE corner is fan slivers radiating from two base-terrain
# apex vertices that sit off the 1 m LiDAR: (246.3,-248.7) +3.57 m and (246.0,-33.5) +1.53 m; every other vertex of
# those slivers is on dtm_1m. Snap SE fan apices (x>90, y<-30, an edge > 30 m long, |z - dtm_1m| > 1 m) to the
# bilinear DTM. Runs BEFORE fix227a so the re-grid taper uses the corrected corners.
import bpy, bmesh
import numpy as np
A=np.load('/workspace/nj-scenes/montclair-state/data/dtm_1m.npy')
def dtm(x,y):
    gx=x+250-0.5; gy=y+250-0.5; i=int(np.floor(gy)); j=int(np.floor(gx)); fy=gy-i; fx=gx-j
    i=min(498,max(0,i)); j=min(498,max(0,j))
    return float(A[i,j]*(1-fx)*(1-fy)+A[i,j+1]*fx*(1-fy)+A[i+1,j]*(1-fx)*fy+A[i+1,j+1]*fx*fy)
t=bpy.data.objects['Terrain_LiDAR_DTM_1m']; me=t.data
bm=bmesh.new(); bm.from_mesh(me)
mv=[]
for v in bm.verts:
    x,y,z=v.co
    if x>90 and y<-30 and -249.9<x<249.9 and -249.9<y<249.9:
        if max((e.calc_length() for e in v.link_edges),default=0)>30:
            dz=z-dtm(x,y)
            if abs(dz)>1.0:
                mv.append((round(x,1),round(y,1),round(dz,2),len(v.link_faces),v.is_boundary)); v.co.z=dtm(x,y)
bm.to_mesh(me); bm.free(); me.update()
print('F227Z snapped apices',len(mv),mv[:20],flush=True)
