# W53k (ws230, found in the probe230f check after fix230a/c): QJ_NE_seam_ramp (terrain GN) offsets the terrain by the z of
# QJ_NE_seam_ramp_field (0 .. -1.81 m over x 212..240, y 160..240), a ramp that pulled the terrain down toward the old
# low/padded NE edge. With the QI/QG patches and the new gap fill now on USGS 3DEP 1 m, it leaves a 1.2 m trench at x ~220,
# y 174..210 (evaluated -1.1..-1.2 m vs 3DEP; QI/QG base meshes there are within 0.01 m of 3DEP). Field verts with
# x >= 205 are set to 0 offset, except within 2 m of Paths_Roads_OSM paving (kept: never bury paving).
import bpy, json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
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
f=bpy.data.objects['QJ_NE_seam_ramp_field']; W=f.matrix_world; I=W.inverted()
n=0; kept=0; mx=0
for v in f.data.vertices:
    w=W@v.co
    if w.x<205 or w.z>-0.01: continue
    if paved(w.x,w.y): kept+=1; continue
    mx=min(mx,w.z); w.z=0.0; v.co=I@w; n+=1
f.data.update()
rep={'field_verts_zeroed':n,'max_offset_removed':round(mx,2),'kept_near_paving':kept}
print('F230D',json.dumps(rep),flush=True)
json.dump(rep,open('/workspace/nj-scenes/montclair-state/scripts/ws230/fix230d_report.json','w'))
