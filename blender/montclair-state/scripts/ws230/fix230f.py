# W53k part 1 (ws230, after fix230d): the QJ ramp field verts left by fix230d (within 2 m of paving) keep the ground
# 1.1-1.3 m UNDER 3DEP beside the NE street (2020 ortho: a 2-lane street with a sidewalk/verge, lot to the east;
# scripts/ws230/ortho_NElot_grid.jpg). That street (Roads_OSM) stands 0.75-1.3 m ABOVE 3DEP, so zeroing the ramp there only
# brings the ground up to 3DEP and still leaves it under the paving. Zero a field vert only where the highest un-ramped ground within 2 m
# (top of the QI/QG/QH patch base meshes, else 3DEP) < (lowest paving within 2 m) - 0.05, i.e. never above any paving. The paving itself is not touched (AGENTS rule 6).
import bpy, json, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
MS='/workspace/nj-scenes/montclair-state/'
P=np.load(MS+'scripts/ws230/dep1m_full_x-280_280_y-280_280_rowS.npy')
def p3(x,y):
    gx=x+280-0.5; gy=y+280-0.5; i=int(np.floor(gy)); j=int(np.floor(gx)); fy=gy-i; fx=gx-j
    return float(P[i,j]*(1-fx)*(1-fy)+P[i,j+1]*fx*(1-fy)+P[i+1,j]*(1-fx)*fy+P[i+1,j+1]*fx*fy)
PV=[]
for o in bpy.data.objects:
    if o.type=='MESH' and any(c.name=='Paths_Roads_OSM' for c in o.users_collection):
        W=o.matrix_world; PV.append(BVHTree.FromPolygons([W@v.co for v in o.data.vertices],[p.vertices[:] for p in o.data.polygons]))
def pavez(x,y):
    zs=[]
    for dx in (-2,0,2):
        for dy in (-2,0,2):
            for b in PV:
                h=b.ray_cast(Vector((x+dx,y+dy,400)),Vector((0,0,-1)))
                if h[0] is not None: zs.append(h[0].z)
    return min(zs) if zs else None
BB=[]
for nm in ('QI_east_edge_LiDAR_terrain_patch','QG_north_strip_LiDAR_terrain_patch','QH_east_fan_LiDAR_terrain_patch'):
    o=bpy.data.objects[nm]; OW=o.matrix_world
    BB.append(BVHTree.FromPolygons([OW@v.co for v in o.data.vertices],[p.vertices[:] for p in o.data.polygons]))
def basez(x,y):   # un-ramped ground = top of the LiDAR patch base meshes (ray-top wins), else 3DEP
    zs=[h[0].z for h in (b.ray_cast(Vector((x,y,400)),Vector((0,0,-1))) for b in BB) if h[0] is not None]
    return max(zs+[p3(x,y)])
f=bpy.data.objects['QJ_NE_seam_ramp_field']; W=f.matrix_world; I=W.inverted()
n=0; kept=0; mx=0
for v in f.data.vertices:
    w=W@v.co
    if w.x<205 or w.z>-0.01: continue
    pz=pavez(w.x,w.y)
    if pz is not None and max(basez(w.x+dx,w.y+dy) for dx in (-2,0,2) for dy in (-2,0,2))>=pz-0.05: kept+=1; continue
    mx=min(mx,w.z); w.z=0.0; v.co=I@w; n+=1
f.data.update()
rep={'field_verts_zeroed':n,'max_offset_removed':round(mx,2),'kept_ground_would_reach_paving':kept}
print('F230F',json.dumps(rep),flush=True)
json.dump(rep,open(MS+'scripts/ws230/fix230f_report.json','w'))
