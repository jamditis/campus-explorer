# W53d residual (ws228, after fix228a/c): the remaining >0.5 m-high samples in the SE corner sit on the fix227x 2 m grid
# vertices that were blended back toward the old (high) sliver surface near the fix227x fan outlines; those outlines are now
# re-gridded at dtm_1m (fix228c), so the blend is no longer needed. Lower-only: interior (non-boundary) terrain vertices in
# x 140..246, y -249..-33.6 whose linked faces are all < 25 m2 (the 2 m grid and the CDT strips next to it; ws228e raised this from 6 after the A1-corner close-up still showed 2-3 m ridges) and that sit > 0.3 m over bilinear dtm_1m are
# set to dtm_1m. No vertex is raised; boundary vertices (welded to the WS60 apron) are untouched.
import bpy, bmesh, json
import numpy as np
A=np.load('/workspace/nj-scenes/montclair-state/data/dtm_1m.npy')
def dtm(x,y):
    gx=x+250-0.5; gy=y+250-0.5; i=int(np.floor(gy)); j=int(np.floor(gx)); fy=gy-i; fx=gx-j
    i=min(498,max(0,i)); j=min(498,max(0,j))
    return float(A[i,j]*(1-fx)*(1-fy)+A[i,j+1]*fx*(1-fy)+A[i+1,j]*(1-fx)*fy+A[i+1,j+1]*fx*fy)
t=bpy.data.objects['Terrain_LiDAR_DTM_1m']; me=t.data
bm=bmesh.new(); bm.from_mesh(me); moved=[]
for v in bm.verts:
    c=v.co
    if not (140<=c.x<=246 and -249<=c.y<=-33.6) or v.is_boundary or not v.link_faces: continue
    if any(f.calc_area()>=25.0 for f in v.link_faces): continue
    z=dtm(c.x,c.y)
    if c.z-z>0.3: moved.append(round(c.z-z,2)); c.z=z
bm.to_mesh(me); bm.free(); me.update()
rep={'lowered':len(moved),'max':max(moved or [0]),'mean':round(sum(moved)/max(1,len(moved)),2)}
print('F228D',json.dumps(rep),flush=True)
json.dump(rep,open('/workspace/nj-scenes/montclair-state/scripts/ws228/fix228d_report.json','w'))
