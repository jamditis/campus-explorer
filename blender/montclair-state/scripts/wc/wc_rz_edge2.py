"""wc: re-lower RZ2 boundary verts left >0.5 cm above WT after the wc_west poke back-off (x55-56,y315-316)."""
import bpy,sys
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from collections import Counter
O=bpy.data.objects; dg=bpy.context.evaluated_depsgraph_get()
WT=O['WT_richardson_west_LiDAR_patch_UNVERIFIED']; RZ=O[[n for n in O.keys() if n.startswith('RZ2_')][0]]
e=WT.evaluated_get(dg); m=e.to_mesh(); B=BVHTree.FromPolygons([WT.matrix_world@v.co for v in m.vertices],[tuple(p.vertices) for p in m.polygons]); e.to_mesh_clear()
ec=Counter()
for p in RZ.data.polygons:
    vs=list(p.vertices)
    for i in range(len(vs)): ec[tuple(sorted((vs[i],vs[(i+1)%len(vs)])))]+=1
mw=RZ.matrix_world; mi=mw.inverted(); k=0
for i in {i for e_,c in ec.items() if c==1 for i in e_}:
    c=mw@RZ.data.vertices[i].co
    if not (44<=c.x<=60 and 305<=c.y<=325): continue
    h=B.ray_cast(Vector((c.x,c.y,500)),Vector((0,0,-1)))
    if h[0] is not None and c.z>h[0].z+0.005: print('fix',round(c.x,1),round(c.y,1),round(c.z-h[0].z,3)); c.z=h[0].z+0.003; RZ.data.vertices[i].co=mi@c; k+=1
RZ.data.update(); print('RZFIX',k)
if '--save' in sys.argv: bpy.ops.wm.save_mainfile(); print('SAVED',len(O))
