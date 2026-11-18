import bpy,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
O=bpy.data.objects
def bv(o): mw=o.matrix_world; return BVHTree.FromPolygons([mw@v.co for v in o.data.vertices],[tuple(p.vertices) for p in o.data.polygons])
A=bv(O['QS_footway_313027436_UNVERIFIED']); B=bv(O['QS_footway_313027437_UNVERIFIED'])
d=[]
for x in np.arange(78,92,0.25):
    for y in np.arange(290,305,0.25):
        a=A.ray_cast(Vector((x,y,500)),Vector((0,0,-1)))[0]; b=B.ray_cast(Vector((x,y,500)),Vector((0,0,-1)))[0]
        if a and b: d.append((x,y,a.z-b.z))
d=np.array(d); print('OV',len(d), d[:,2].min() if len(d) else 0, np.median(d[:,2]) if len(d) else 0, d[:,2].max() if len(d) else 0)
m=O['QT_walk_concrete_joints_UNVERIFIED'] if 'QT_walk_concrete_joints_UNVERIFIED' in O else None
mat=bpy.data.materials['QT_walk_concrete_joints_UNVERIFIED']
print('NODES',[(n.type,n.name) for n in mat.node_tree.nodes])
