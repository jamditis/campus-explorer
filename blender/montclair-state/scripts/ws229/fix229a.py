# W53g (ws229): the QI_east_edge_LiDAR_terrain_patch mesh (joined into Terrain_LiDAR_DTM_1m by the QI modifier, ray-top wins)
# still carries the old blend toward the former high base sheet along its south band (y -60..-20): verts up to +2.3 m over
# dtm_1m, e.g. (205,-45) patch 96.38 vs dtm 94.14 / 3DEP 94.16 (dsm 109.5 = canopy, so the patch is neither ground nor
# canopy). The base it blended to was re-gridded to dtm_1m in ws227/ws228. Bare terrain (no paving in the patch mesh):
# patch verts in x 86..246, y -60.5..-20 that sit > 0.3 m over bilinear dtm_1m are set to dtm_1m. Lower-only, terrain only.
import bpy, json
import numpy as np
A=np.load('/workspace/nj-scenes/montclair-state/data/dtm_1m.npy')
D=np.load('/workspace/nj-scenes/montclair-state/data/skirt_dem_10m.npy')
def dtm(x,y):
    gx=x+250-0.5; gy=y+250-0.5; i=int(np.floor(gy)); j=int(np.floor(gx)); fy=gy-i; fx=gx-j
    i=min(498,max(0,i)); j=min(498,max(0,j))
    return float(A[i,j]*(1-fx)*(1-fy)+A[i,j+1]*fx*(1-fy)+A[i+1,j]*(1-fx)*fy+A[i+1,j+1]*fx*fy)
def d3(x,y): return float(D[int((2000-y)/10), int((x+2000)/10)])
o=bpy.data.objects['QI_east_edge_LiDAR_terrain_patch']; me=o.data; mw=o.matrix_world; inv=mw.inverted()
moved=[]; agree=0
for v in me.vertices:
    w=mw@v.co
    if not (86<=w.x<=246 and -60.5<=w.y<=-20): continue
    z=dtm(w.x,w.y)
    if w.z-z>0.3:
        moved.append(round(w.z-z,2))
        if w.z-d3(w.x,w.y)>0.3: agree+=1
        w.z=z; v.co=inv@w
me.update()
rep={'lowered':len(moved),'max':max(moved or [0]),'mean':round(sum(moved)/max(1,len(moved)),2),'3dep_also_high':agree}
print('F229A',json.dumps(rep),flush=True)
json.dump(rep,open('/workspace/nj-scenes/montclair-state/scripts/ws229/fix229a_report.json','w'))
