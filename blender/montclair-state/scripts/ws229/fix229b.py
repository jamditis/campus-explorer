# W53g (ws229): interior SE base-terrain verts (x 140..246, y -249..-60, not boundary, linked faces all < 25 m2 = the
# ws227/ws228 2 m grid and CDT strips) that sit > 0.3 m UNDER bilinear dtm_1m are raised to dtm_1m (bare terrain; mirrors
# fix228d, which lowered the high ones). Boundary verts welded to the WS60 apron are untouched.
import bpy, bmesh, json
import numpy as np
A=np.load('/workspace/nj-scenes/montclair-state/data/dtm_1m.npy')
def dtm(x,y):
    gx=x+250-0.5; gy=y+250-0.5; i=int(np.floor(gy)); j=int(np.floor(gx)); fy=gy-i; fx=gx-j
    i=min(498,max(0,i)); j=min(498,max(0,j))
    return float(A[i,j]*(1-fx)*(1-fy)+A[i,j+1]*fx*(1-fy)+A[i+1,j]*(1-fx)*fy+A[i+1,j+1]*fx*fy)
t=bpy.data.objects['Terrain_LiDAR_DTM_1m']; me=t.data
bm=bmesh.new(); bm.from_mesh(me); moved=[]; big=[]
for v in bm.verts:
    c=v.co
    if not (140<=c.x<=246 and -249<=c.y<=-60) or v.is_boundary or not v.link_faces: continue
    z=dtm(c.x,c.y)
    if z-c.z>0.3:
        if any(f.calc_area()>=25.0 for f in v.link_faces): big.append((round(c.x),round(c.y),round(z-c.z,2))); continue
        moved.append(round(z-c.z,2)); c.z=z
bm.to_mesh(me); bm.free(); me.update()
rep={'raised':len(moved),'max':max(moved or [0]),'mean':round(sum(moved)/max(1,len(moved)),2),'skipped_bigface':big[:40],'n_skipped':len(big)}
print('F229B',json.dumps(rep),flush=True)
json.dump(rep,open('/workspace/nj-scenes/montclair-state/scripts/ws229/fix229b_report.json','w'))
