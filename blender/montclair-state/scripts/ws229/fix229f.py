# W53i (ws229, found in the W53g close-up self-review): north of A2 (y > -33.4) the WS60 edge apron stands 1.5-6 m over the
# 1 m LiDAR along the east scene edge (a long slanted sheet in the eye/close-up views). There is no base terrain left there
# (deleted under the QI LiDAR patch, whose east edge is at x ~246), so the apron's inner edge still carries the old base
# height. Per apron row (verts grouped by y): the inner (min-x) vertex goes to dtm_1m (bilinear), the outer (max-x) vertex
# stays (it meets the skirt), and the verts between are set linear in x between them (same as fix228e south of A2).
# Rows y in (-33.4, 185); the dtm_1m NE corner beyond y 185 is padded, so it is left alone.
import bpy, json, collections, numpy as np
A=np.load('/workspace/nj-scenes/montclair-state/data/dtm_1m.npy')
def dtm(x,y):
    gx=min(249.49,x)+250-0.5; gy=y+250-0.5; i=int(np.floor(gy)); j=int(np.floor(gx)); fy=gy-i; fx=gx-j
    i=min(498,max(0,i)); j=min(498,max(0,j))
    return float(A[i,j]*(1-fx)*(1-fy)+A[i,j+1]*fx*(1-fy)+A[i+1,j]*(1-fx)*fy+A[i+1,j+1]*fx*fy)
ap=bpy.data.objects['WS60_terrain_edge_apron_LiDAR_to_skirt']; me=ap.data; W=ap.matrix_world; inv=W.inverted()
rows=collections.defaultdict(list)
for v in me.vertices:
    w=W@v.co
    if w.x>235 and -33.4<w.y<185: rows[round(w.y,1)].append(v)
dzi=[]; nmid=0; skipped=0
for y,vs in rows.items():
    ws=sorted(((W@v.co),v) for v in vs) if False else sorted([(W@v.co,v) for v in vs],key=lambda p:p[0].x)
    if len(ws)<2 or ws[-1][0].x-ws[0][0].x<5: skipped+=1; continue
    wi,vi=ws[0]; wo,vo=ws[-1]
    zi=dtm(wi.x,wi.y); dzi.append(round(wi.z-zi,2))
    for w,v in ws[:-1]:
        if abs(w.x-wi.x)<0.3: nz=zi
        else: nz=zi+(wo.z-zi)*(w.x-wi.x)/(wo.x-wi.x); nmid+=1
        w2=w.copy(); w2.z=nz; v.co=inv@w2
me.update()
rep={'rows':len(rows),'skipped':skipped,'inner_dz_before':[min(dzi or [0]),max(dzi or [0])],'inner_mean':round(sum(dzi)/max(1,len(dzi)),2),'mid_set':nmid}
print('F229F',json.dumps(rep),flush=True)
json.dump(rep,open('/workspace/nj-scenes/montclair-state/scripts/ws229/fix229f_report.json','w'))
