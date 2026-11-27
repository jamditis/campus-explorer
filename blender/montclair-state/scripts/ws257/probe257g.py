# ws257 read-only: why is the 4 km skirt 3 m below the WS110 patch's S edge (y -300)? skirt base vs evaluated z, patch z, along N-S lines
import sys; sys.stdout.reconfigure(line_buffering=True)
import bpy, os, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
MS='/workspace/nj-scenes/montclair-state/'
P='WS110_ground_patch_S_of_y-238_DTM2023_1m_lawn_UNVERIFIED'; S='Context_skirt_3DEP_ortho_4km'
with bpy.data.libraries.load(MS+'montclair_state.blend') as (a,b): b.objects=[P,S]+[n for n in a.objects if n.startswith('WS172_skirt_target')]
for o in b.objects: bpy.context.scene.collection.objects.link(o)
sk=bpy.data.objects[S]; print('P257G skirt mods',[(m.name,m.type,m.show_render, m.node_group.name if m.type=='NODES' and m.node_group else '') for m in sk.modifiers])
dg=bpy.context.evaluated_depsgraph_get()
X0,X1,Y0,Y1=-320,-130,-330,-280
def bv(o,evald):
    me=o.evaluated_get(dg).to_mesh() if evald else o.data; M=o.matrix_world; vs=[M@v.co for v in me.vertices]
    ps=[p.vertices[:] for p in me.polygons if any(X0<vs[i].x<X1 and Y0<vs[i].y<Y1 for i in p.vertices)]
    return BVHTree.FromPolygons(vs,ps)
SB=bv(sk,False); SE=bv(sk,True); PB=bv(bpy.data.objects[P],True)
def z(bt,x,y):
    h=bt.ray_cast(Vector((x,y,400)),Vector((0,0,-1)),600); return round(h[0].z,2) if h[0] else None
for x in (-290,-270,-250,-230,-210,-190,-170,-155):
    print('P257G x',x,[(y,z(PB,x,y),z(SB,x,y),z(SE,x,y)) for y in (-296,-299,-299.8,-300.5,-302,-305,-310,-320)])
os._exit(0)
