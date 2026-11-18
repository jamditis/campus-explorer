import bpy,sys,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
print('P195 py',sys.version)
try:
    sys.path.insert(0,'/workspace/nj-scenes/pylib_shapely313'); import shapely; print('P195 shapely',shapely.__version__)
except Exception as e: print('P195 shapely ERR',e)
o=bpy.data.objects['WS77_lot_median_island_MULCH_JOEphoto20261112_curb_ortho2020']
print('P195 mats',[m.name if m else None for m in o.data.materials],'mods',[m.name for m in o.modifiers],'parent',o.parent,'children',[c.name for c in o.children])
W=np.array([tuple(o.matrix_world@v.co) for v in o.data.vertices])
from collections import Counter
print('P195 mat faces',Counter(p.material_index for p in o.data.polygons))
for mi in set(p.material_index for p in o.data.polygons):
    zs=[W[v][2] for p in o.data.polygons if p.material_index==mi for v in p.vertices]; print('P195 mi',mi,'z',min(zs),max(zs))
lots=[ob for ob in bpy.data.objects if ob.type=='MESH' and any(ob.name.startswith(p) for p in ('WS75_sprague_lot_asphalt','WS76_accessible_lot_asphalt','WS80_sprague_lot_fill'))]
for ob in lots:
    mw=ob.matrix_world; B=BVHTree.FromPolygons([mw@v.co for v in ob.data.vertices],[p.vertices[:] for p in ob.data.polygons])
    for xy in [(-235,-87.5),(-254.5,-87.8),(-214,-92),(-255.5,-82),(-250,-84)]:
        h=B.ray_cast(Vector((xy[0],xy[1],300)),Vector((0,0,-1))); print('P195',ob.name[:20],xy,h[0] and round(h[0].z,3),[m.name for m in ob.data.materials][:2])
# z of island near foot vs lot just outside
import bmesh
for ob in bpy.data.objects:
    if ob.type=='MESH' and not ob.hide_render:
        bb=[ob.matrix_world@Vector(c) for c in ob.bound_box]
        xs=[p.x for p in bb]; ys=[p.y for p in bb]
        if min(xs)>-262 and max(xs)<-206 and min(ys)>-102 and max(ys)<-74: print('P195 local obj',ob.name,len(ob.data.vertices))
