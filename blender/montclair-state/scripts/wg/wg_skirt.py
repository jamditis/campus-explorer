import bpy, numpy as np, os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ng=bpy.data.node_groups['WF_skirt_under_east_dorm_patch']
# print links around compare 005/006 for understanding
for l in ng.links:
    if l.to_node.name in ('Compare.005','Compare.006','Boolean Math.004','Boolean Math.005','Set Position') or l.from_node.name in ('Compare.005','Compare.006'):
        print(l.from_node.name,l.from_socket.name,'->',l.to_node.name,l.to_socket.name)
c=ng.nodes['Compare.005']; print('op',c.operation,c.data_type, [i.default_value for i in c.inputs if i.enabled and not i.is_linked])
for i in c.inputs:
    if i.enabled and not i.is_linked and i.name=='B': i.default_value=-1.5
ng['wg_note']='Compare.005 B -0.5 -> -1.5 (wg landing pad grade)'
bpy.context.view_layer.update()
def bvh(o):
    dg=bpy.context.evaluated_depsgraph_get(); e=o.evaluated_get(dg); m=e.to_mesh()
    t=BVHTree.FromPolygons([o.matrix_world@v.co for v in m.vertices],[tuple(p.vertices) for p in m.polygons]); e.to_mesh_clear(); return t
bp=bvh(bpy.data.objects['WF_east_dorm_LiDAR_terrain_patch_UNVERIFIED']); bs=bvh(bpy.data.objects['Context_skirt_3DEP_ortho_4km'])
g=lambda t,x,y:(lambda h:h[0].z if h[0] else None)(t.ray_cast(Vector((x,y,400)),Vector((0,0,-1))))
out=[]
for x in np.arange(209,216.2,0.25):
    for y in np.arange(399,412,0.25):
        a=g(bp,x,y); b=g(bs,x,y)
        if a and b and b-a>0.0:
            inpad=(213.9<=x<=216.15 and 403.1<=y<=408.1)
            out.append((x,y,round(b-a,3),inpad))
print('pokes',len(out),'outside pad',[o for o in out if not o[3]][:30])
print('max outside', max([o[2] for o in out if not o[3]] or [0]))
bpy.ops.wm.save_mainfile(); print('SAVED')
