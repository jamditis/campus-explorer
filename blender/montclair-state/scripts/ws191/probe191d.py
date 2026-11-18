# ws191 coverage map E of the WS170b strip end: '.'=visible top, 'X'=only skirt (target says ground), 'o'=nothing
import bpy, bmesh, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
X0,X1,Y0,Y1=-301.0,-288.0,-240.0,-233.0
T=[];TG=None
for o in bpy.data.objects:
    if o.type!='MESH' or o.name.startswith(('Context_','BD_','Terrain_LiDAR')): continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    if max(v.x for v in bb)<X0 or min(v.x for v in bb)>X1 or max(v.y for v in bb)<Y0 or min(v.y for v in bb)>Y1: continue
    if any(k in o.name for k in ('tree','Tree','util','pole','lamp','Lamp')): continue
    bm=bmesh.new(); bm.from_mesh(o.data); bm.transform(o.matrix_world); t=BVHTree.FromBMesh(bm); bm.free()
    hid=o.hide_render or any(c.hide_render for c in o.users_collection)
    if 'WS163_skirt_target' in o.name: TG=t
    elif not hid: T.append((o.name,t)); print('OBJ',o.name)
for y in np.arange(Y1,Y0,-0.4):
    s=''
    for x in np.arange(X0,X1,0.4):
        top=[t.ray_cast(Vector((x,y,300)),Vector((0,0,-1)))[0] for _,t in T]; top=[h for h in top if h]
        tg=TG.ray_cast(Vector((x,y,300)),Vector((0,0,-1)))[0]
        s+='.' if top else ('X' if tg else 'o')
    print('ROW %.1f %s'%(y,s))
