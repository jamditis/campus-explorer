"""we: x54-60,y280-295 'ground gap' check: are the no-ground cells inside the MO Health Drop-In Center footprint, and does the building reach the ground?"""
import bpy,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
O=bpy.data.objects; dg=bpy.context.evaluated_depsgraph_get()
def bvh(o):
    e=o.evaluated_get(dg); m=e.to_mesh(); b=BVHTree.FromPolygons([o.matrix_world@v.co for v in m.vertices],[tuple(p.vertices) for p in m.polygons]); e.to_mesh_clear(); return b
H=[o for o in O if o.name.startswith('MO Health Drop-In')]
for o in H:
    c=np.array([o.matrix_world@Vector(b) for b in o.bound_box]); print('OBJ',o.name,c.min(0).round(2),c.max(0).round(2),flush=True)
HB=[bvh(o) for o in H if o.type=='MESH']
GRDn=[n for n in O.keys() if O[n].type=='MESH' and n.startswith(('WV_stone','WN_south','WO_gully','Terrain_LiDAR','QW_DTM','WU_rich','WT_rich','WF_east','RZ2_','WA0_','SA_ground_lower_patch'))]
G=[bvh(O[n]) for n in GRDn]
def top(B,x,y,z0=500):
    z=[h[0].z for b in B for h in [b.ray_cast(Vector((x,y,z0)),Vector((0,0,-1)))] if h[0] is not None]; return max(z) if z else None
inside=outside=0; out=[]
for x in np.arange(54,60.01,0.5):
    for y in np.arange(280,295.01,0.5):
        if top(G,x,y) is not None: continue
        if top(HB,x,y) is not None: inside+=1
        else: outside+=1; out.append((x,y))
print('NOGROUND inside_building',inside,'outside',outside,out[:20],flush=True)
# horizontal rays at ground+5cm from outside toward the building: does anything let light under? sample the lowest building z near perimeter
w=[o for o in H if 'walls' in o.name][0]; e=w.evaluated_get(dg); m=e.to_mesh(); zs=np.array([(w.matrix_world@v.co).z for v in m.vertices]); e.to_mesh_clear()
print('WALL zmin',zs.min().round(3),flush=True)
