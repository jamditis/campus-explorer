import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
src='/workspace/nj-scenes/montclair-state/montclair_state.blend'
P=('WS75_sprague_lot_asphalt','WS76_accessible_lot_asphalt','WS74_cogen_lot','WS68_RHD_ground','Terrain_LiDAR_DTM_1m','WS77_lot_median')
with bpy.data.libraries.load(src) as (fr,to): names=[n for n in fr.objects if n.startswith(P)]
with bpy.data.libraries.load(src,link=False) as (fr,to): to.objects=names
objs=[o for o in to.objects if o and o.type=='MESH']
T=[]
for o in objs:
    dg=None
    mw=o.matrix_world; V=[mw@v.co for v in o.data.vertices]
    T.append((o.name[:6],BVHTree.FromPolygons(V,[tuple(f.vertices) for f in o.data.polygons])))
    print('WS78P obj',o.name,len(V),[m.name+':'+m.type for m in o.modifiers],flush=True)
def hits(x,y):
    r=[]
    for n,t in T:
        loc,nn,i,d=t.ray_cast(Vector((x,y,400)),Vector((0,0,-1)))
        if loc: r.append((n,round(loc.z,2)))
    return r
for y in (-70,-74,-78,-82,-86,-90,-94,-98):
    for x in range(-272,-226,3):
        print('WS78P',x,y,hits(x,y),flush=True)
