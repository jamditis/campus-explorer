# ws230 (after fix230a): re-seat trees whose trunk base (local z~0 ring, as fix226b/fix228b) stands on the new
# WS230 gap fill or the re-heighted WS60 east strip: trunk base -> that ground - 0.05 m (both ways).
import bpy, json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
G=[]
for nm in ('WS230_NE_east_gap_fill_3DEP_UNVERIFIED','WS60_terrain_edge_apron_LiDAR_to_skirt'):
    o=bpy.data.objects[nm]; W=o.matrix_world
    G.append(BVHTree.FromPolygons([W@v.co for v in o.data.vertices],[p.vertices[:] for p in o.data.polygons]))
def gz(x,y):
    b=G[0] if x<246 else G[1]   # fill west of x 246, the WS60 strip east of it
    h=b.ray_cast(Vector((x,y,400)),Vector((0,0,-1))); return None if h[0] is None else h[0].z
tr=[]
for o in bpy.data.objects:
    if o.type!='MESH' or o.hide_render or o.parent is not None or not o.data.name.startswith('Tree_') or not o.name.startswith('T_'): continue
    lo=o.matrix_world.translation
    if not (212<lo.x<280 and -12<lo.y<250): continue
    ring=[o.matrix_world@v.co for v in o.data.vertices if abs(v.co.z)<0.03]
    if len(ring)<3: continue
    x=sum(p.x for p in ring)/len(ring); y=sum(p.y for p in ring)/len(ring); z=min(p.z for p in ring)
    g=gz(x,y)
    if g is None: continue
    dz=(g-0.05)-z
    if abs(dz)>0.03: o.location.z+=dz; tr.append((o.name,round(x,1),round(y,1),round(dz,2)))
rep={'trees_reseated':tr}
print('F230B',json.dumps(rep),flush=True)
json.dump(rep,open('/workspace/nj-scenes/montclair-state/scripts/ws230/fix230b_report.json','w'))
