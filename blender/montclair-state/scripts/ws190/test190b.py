exec(open('/workspace/nj-scenes/montclair-state/scripts/ws190/fix190b.py').read())
import bpy, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
vl=bpy.context.view_layer
objs=[]
for o in bpy.data.objects:
    if o.type!='MESH' or o.name.startswith(('Context_skirt','BD_','MID_','WS165','WS166','WS48')) or o.hide_render: continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]; xs=[v.x for v in bb]; ys=[v.y for v in bb]
    if max(xs)<-305 or min(xs)>-301 or max(ys)<-238 or min(ys)>-234.5 or len(o.data.vertices)>500000: continue
    if o.name in vl.objects and not o.visible_get(): continue
    M=o.matrix_world; objs.append((o.name,BVHTree.FromPolygons([M@v.co for v in o.data.vertices],[p.vertices[:] for p in o.data.polygons])))
for y in np.arange(-234.6,-237.81,-0.2):
    row=''
    for x in np.arange(-305,-300.99,0.2):
        hs=[(h[0].z,n) for n,t in objs for h in [t.ray_cast(Vector((x,y,200)),Vector((0,0,-1)))] if h[0]]
        if not hs: row+='.'; continue
        n=max(hs)[1]; row+=next((c for k,c in (('WS190b','f'),('WS163_ground','g'),('WS163_Lot3','A'),('WS170b','C'),('WS162_Lot3_asphalt','L'),('WS162_Lot3_S_end','F')) if n.startswith(k)),'?')
    print('R190B %.1f %s'%(y,row))
