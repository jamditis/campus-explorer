# ws249: which ground objects cover the soccer field's WEST side (x -340..-250, y -20..220), and how their BASE meshes
# (modifiers off, merge208-style load) compare with 2023 LiDAR class-2 ground (g1m_w23.npy). Read-only.
import bpy, numpy as np, re, sys, os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
@bpy.app.handlers.persistent
def _off(*a):
    for o in bpy.data.objects:
        for m in o.modifiers: m.show_viewport=False
bpy.app.handlers.load_post.append(_off)
bpy.ops.wm.open_mainfile(filepath='/workspace/nj-scenes/montclair-state/montclair_state.blend')
G=np.load('/workspace/nj-scenes/montclair-state/scripts/ws249/g1m_w23.npy'); X0,Y0=-340.,-20.
pat=re.compile(os.environ.get('PAT','terrain|dtm|ground|skirt|lawn|turf|pitch|field|grass|fill|apron'),re.I)
for o in bpy.data.objects:
    if o.type!='MESH' or o.hide_render or not pat.search(o.name): continue
    M=o.matrix_world; bb=[M@Vector(c) for c in o.bound_box]
    if max(v.x for v in bb)<-340 or min(v.x for v in bb)>-250 or max(v.y for v in bb)<-20 or min(v.y for v in bb)>220: continue
    me=o.data; vs=[M@v.co for v in me.vertices]
    t=BVHTree.FromPolygons(vs,[p.vertices[:] for p in me.polygons])
    R=[]
    for y in np.arange(-18,218,4.0):
        for x in np.arange(-338,-252,4.0):
            h=t.ray_cast(Vector((x,y,400)),Vector((0,0,-1)),600)
            if h[0] is None: continue
            l=G[int(y-Y0),int(x-X0)]
            if np.isfinite(l): R.append((x,y,h[0].z-l))
    mods=[m.name for m in o.modifiers]
    if R:
        d=np.array(R)[:,2]
        print('W249',o.name,'n',len(R),'med %.2f p5 %.2f p95 %.2f'%(np.median(d),np.percentile(d,5),np.percentile(d,95)),'mods',mods[:6],flush=True)
        np.save('/tmp/w249_%s.npy'%re.sub(r'\W','_',o.name)[:60],np.array(R))
    else: print('W249',o.name,'no hits',flush=True)
sys.stdout.flush(); os._exit(0)
