import bpy, sys, os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
os.environ['DRY']='1'
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws226/fix226a.py').read().split('B1,nv1=terrain_bvh()')[0])
def ev(upto=None):
    for m in t.modifiers: m.show_viewport=m.show_render
    if upto:
        k=False
        for m in t.modifiers:
            if k: m.show_viewport=False
            if m.name==upto: k=True
    dg=bpy.context.evaluated_depsgraph_get(); e=t.evaluated_get(dg); me=e.to_mesh()
    B=BVHTree.FromPolygons([v.co.copy() for v in me.vertices],[p.vertices[:] for p in me.polygons]); e.to_mesh_clear(); return B
def allz(B,x,y):
    z=400; hs=[]
    while len(hs)<4:
        h=B.ray_cast(Vector((x,y,z)),Vector((0,0,-1)))
        if not h[0]: break
        hs.append(round(h[0].z,2)); z=h[0].z-0.02
    return hs
PT=[(200,150),(230,50),(180,60),(160,100),(140,100)]
for up in ('QI_east_edge_LiDAR_patch','WS226_drop_base_under_LiDAR_patches',None):
    B=ev(up); print('P226D',up,[allz(B,x,y) for x,y in PT],flush=True)
sys.stdout.flush(); os._exit(0)
