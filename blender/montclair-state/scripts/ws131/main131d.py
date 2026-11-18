# ws131 self-review fix 2: the W-foot mulch bed's E end stood ~0.3 m above the ground under the unmodelled E building
# (dark skirt cliff in the eye view from E) -> bed surface feathered down to the ground over x -177.3..-175.4.
import bpy, os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
b=[o for o in bpy.data.objects if o.name.startswith('WS131_E_building_W_foot_mulch_bed')][0]
gs=[o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith(('Terrain_LiDAR_DTM_1m','WS113_terrain_fan_fill','WS110_ground_patch'))]
T=[BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[p.vertices for p in o.data.polygons]) for o in gs]
def zg(x,y):
    best=None
    for t in T:
        h=t.ray_cast(Vector((x,y,200)),Vector((0,0,-1)))
        if h[0] is not None: best=h[0].z if best is None else max(best,h[0].z)
    return best
# group verts by (x,y) column; top = max z
cols={}
for v in b.data.vertices: cols.setdefault((round(v.co.x,3),round(v.co.y,3)),[]).append(v)
n=0
for (x,y),vs in cols.items():
    if x<=-177.3: continue
    top=max(v.co.z for v in vs); g=zg(-174.9,y)
    if g is None: continue
    w=min(1.0,(x+177.3)/1.9); d=w*max(0.0,top-(g+0.01))
    for v in vs: v.co.z-=d
    n+=1
b.data.update(); print('M131d bed columns feathered',n)
if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('M131d SAVED')
