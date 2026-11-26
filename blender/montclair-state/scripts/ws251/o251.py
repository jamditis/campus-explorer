# ws249: objects standing on the W slope (x -340..-282, y 92..216): base z (lowest world bbox z for meshes, origin z for
# empties/instancers) vs the NEW evaluated PK ground and the OLD (snap off) ground. Read-only.
import bpy, sys, os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
@bpy.app.handlers.persistent
def _off(*a):
    for o in bpy.data.objects:
        for m in o.modifiers: m.show_viewport=False
bpy.app.handlers.load_post.append(_off)
bpy.ops.wm.open_mainfile(filepath='/workspace/nj-scenes/montclair-state/'+os.environ.get('F','montclair_state_ws250q.blend'))
PK=bpy.data.objects['Terrain_LiDAR_DTM_1m']
def bv():
    dg=bpy.context.evaluated_depsgraph_get(); e=PK.evaluated_get(dg); me=e.to_mesh(); M=PK.matrix_world
    t=BVHTree.FromPolygons([M@v.co for v in me.vertices],[p.vertices[:] for p in me.polygons]); return t
for m in PK.modifiers: m.show_viewport=True
NEW=bv(); OLD=NEW
def gz(t,x,y):
    h=t.ray_cast(Vector((x,y,400)),Vector((0,0,-1)),600); return None if h[0] is None else h[0].z
for o in bpy.data.objects:
    if o.name.startswith(('PK_','WS250_','WS251_','Context_','BD_')) or o.hide_render and o.type=='MESH': continue
    M=o.matrix_world
    if o.type=='MESH':
        bb=[M@Vector(c) for c in o.bound_box]; cx=sum(v.x for v in bb)/8; cy=sum(v.y for v in bb)/8; z=min(v.z for v in bb)
        if max(v.x for v in bb)-min(v.x for v in bb)>40 or max(v.y for v in bb)-min(v.y for v in bb)>40: continue
    elif o.type=='EMPTY' and o.instance_type=='COLLECTION': cx,cy,z=M.translation
    else: continue
    if not (-195<cx<-163 and 139<cy<179): continue
    n=gz(NEW,cx,cy); od=gz(OLD,cx,cy)
    if n is None: continue
    print('O251 %-48s %-6s c(%.1f,%.1f) base %.2f new %.2f old %.2f  base-new %+.2f'%(o.name[:48],o.type,cx,cy,z,n,od if od else -1,z-n),flush=True)
sys.stdout.flush(); os._exit(0)
