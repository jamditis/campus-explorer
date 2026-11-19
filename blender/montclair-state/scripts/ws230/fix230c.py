# W53j part 2 (ws230, runs BEFORE fix230a): inside the QI LiDAR patch, verts whose dtm_1m cell is edge-PADDED (constant
# runs, scripts/ws230/pad_mask230.npy, components >= 30 cells) and that sit > 0.3 m off USGS 3DEP 1 m are set to 3DEP
# (bilinear), both ways (also where dtm_1m itself is > 0.5 m off 3DEP: 3DEP agrees with dtm_1m within ~0.1 m wherever
# dtm_1m is real, so a larger disagreement marks padding the run detector missed): e.g. (226,102) +2.2 m, (232,78) -1.1 m, (220,190) -1.2 m. Only x > 150, and never within 2 m of
# any Paths_Roads_OSM paving (none there; check kept so no paving is buried or undercut). Terrain only.
import bpy, json
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
MS='/workspace/nj-scenes/montclair-state/'
P=np.load(MS+'scripts/ws230/dep1m_full_x-280_280_y-280_280_rowS.npy'); PAD=np.load(MS+'scripts/ws230/pad_mask230.npy')
def p3(x,y):
    gx=x+280-0.5; gy=y+280-0.5; i=int(np.floor(gy)); j=int(np.floor(gx)); fy=gy-i; fx=gx-j
    return float(P[i,j]*(1-fx)*(1-fy)+P[i,j+1]*fx*(1-fy)+P[i+1,j]*(1-fx)*fy+P[i+1,j+1]*fx*fy)
A=np.load(MS+'data/dtm_1m.npy')
def dtm(x,y):
    gx=x+250-0.5; gy=y+250-0.5; i=min(498,max(0,int(np.floor(gy)))); j=min(498,max(0,int(np.floor(gx)))); fy=min(1,max(0,gy-i)); fx=min(1,max(0,gx-j))
    return float(A[i,j]*(1-fx)*(1-fy)+A[i,j+1]*fx*(1-fy)+A[i+1,j]*(1-fx)*fy+A[i+1,j+1]*fx*fy)
PV=[]
for o in bpy.data.objects:
    if o.type=='MESH' and any(c.name=='Paths_Roads_OSM' for c in o.users_collection):
        W=o.matrix_world; PV.append(BVHTree.FromPolygons([W@v.co for v in o.data.vertices],[p.vertices[:] for p in o.data.polygons]))
def paved(x,y):
    for dx in (-2,0,2):
        for dy in (-2,0,2):
            for b in PV:
                if b.ray_cast(Vector((x+dx,y+dy,400)),Vector((0,0,-1)))[0] is not None: return True
    return False
qi=bpy.data.objects['QI_east_edge_LiDAR_terrain_patch']; W=qi.matrix_world; I=W.inverted()
mv=[]; skip=0; big=[]; sk=[]
for v in qi.data.vertices:
    w=W@v.co
    if w.x<=150 or not (-250<w.x<249.5 and -250<w.y<249.5): continue
    z=p3(w.x,w.y)
    if not (PAD[int(w.y+250),int(w.x+250)] or abs(dtm(w.x,w.y)-z)>0.5): continue
    if abs(w.z-z)<=0.3: continue
    if paved(w.x,w.y): skip+=1; sk.append((round(w.x),round(w.y),round(w.z-z,1))); continue
    mv.append(round(w.z-z,2))
    if abs(w.z-z)>1: big.append((round(w.x),round(w.y),round(w.z-z,1)))
    w.z=z; v.co=I@w
qi.data.update()
rep={'qi_verts_to_3dep':len(mv),'lowered':sum(1 for d in mv if d>0),'raised':sum(1 for d in mv if d<0),'max_down':max(mv or [0]),'max_up':-min(mv or [0]),'skipped_near_paving':skip,'big_moves':big[:80],'skipped':sk[:60]}
print('F230C',json.dumps(rep),flush=True)
json.dump(rep,open(MS+'scripts/ws230/fix230c_report.json','w'))
