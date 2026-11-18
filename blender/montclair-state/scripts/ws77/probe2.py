import bpy
from mathutils import Vector
src='/workspace/nj-scenes/montclair-state/montclair_state.blend'
with bpy.data.libraries.load(src) as (fr,to): names=[n for n in fr.objects if n.startswith(('WS75_sprague_lot_asphalt','WS76_accessible_lot_asphalt','WS68_RHD_ground'))]
with bpy.data.libraries.load(src,link=False) as (fr,to): to.objects=names
objs=[o for o in to.objects if o]
for o in objs: print('WS77P obj',o.name[:40],len(o.data.vertices),[round(v,2) for v in (min((o.matrix_world@Vector(c)).z for c in o.bound_box),max((o.matrix_world@Vector(c)).z for c in o.bound_box))],flush=True)
from mathutils.bvhtree import BVHTree
T=[]
for o in objs:
    mw=o.matrix_world; V=[mw@v.co for v in o.data.vertices]; T.append((o.name[:4],BVHTree.FromPolygons(V,[tuple(f.vertices) for f in o.data.polygons])))
def hits(x,y):
    r=[]
    for n,t in T:
        loc,nn,i,d=t.ray_cast(Vector((x,y,300)),Vector((0,0,-1)))
        if loc: r.append((n,round(loc.z,2)))
    return r
def _old(x,y):
    r=[]
    for o in objs:
        mi=o.matrix_world.inverted(); a=mi@Vector((x,y,300)); b=mi@Vector((x,y,0))
        ok,loc,n,i=o.ray_cast(a,(b-a).normalized())
        if ok: r.append((o.name[:4],round((o.matrix_world@loc).z,2)))
    return r
for x in (-254,-245,-237,-228,-218):
    for y in range(-78,-99,-2):
        print('WS77P',x,y,hits(x,y),flush=True)
