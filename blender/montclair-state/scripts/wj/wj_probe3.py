import bpy, numpy as np, json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
sk=bpy.data.objects['Context_skirt_3DEP_ortho_4km']
dg=bpy.context.evaluated_depsgraph_get()
e=sk.evaluated_get(dg); m=e.to_mesh(); vs=[sk.matrix_world@v.co for v in m.vertices]
b=BVHTree.FromPolygons(vs,[tuple(p.vertices) for p in m.polygons]); e.to_mesh_clear()
S=np.full((55,110),np.nan)
for j in range(55):
    for i in range(110):
        h=b.ray_cast(Vector((150.5+i,290.5+j,400)),Vector((0,0,-1)))
        if h[0] is not None: S[j,i]=h[0].z
np.save('/workspace/nj-scenes/montclair-state/data/wj/skirt_south.npy',S)
# other objects (non-tree) in x150-260 y290-320
for o in bpy.data.objects:
    if o.type!='MESH' or o.hide_render or o.name.startswith('TL_tree'): continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    x0=min(v.x for v in bb);x1=max(v.x for v in bb);y0=min(v.y for v in bb);y1=max(v.y for v in bb)
    if x1>150 and x0<260 and y1>285 and y0<322 and (x1-x0)<600: print('OBJ',o.name,round(x0),round(x1),round(y0),round(y1),round(min(v.z for v in bb),1))
