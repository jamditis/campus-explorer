# ws235 read-only: step between main-native ground edges (PK fill, WS68, WS60 apron) and the M3b corridor patch, evaluated.
import bpy, mathutils, collections
from mathutils.bvhtree import BVHTree
F='/workspace/nj-scenes/montclair-state/montclair_state_ws236b.blend'
M='M3b_north_LiDAR_DTM_1m_west_rail_corridor_UNVERIFIED_seam'
GS=['PK_Feliciano_west_DTM_fill_UNVERIFIED','WS60_terrain_edge_apron_LiDAR_to_skirt']
with bpy.data.libraries.load(F) as (a,b): b.objects=[M]+GS+[n for n in a.objects if n.startswith('WS68_RHD_ground')]
for o in b.objects: bpy.context.scene.collection.objects.link(o)
dg=bpy.context.evaluated_depsgraph_get()
def ev(o):
    m=bpy.data.meshes.new_from_object(o.evaluated_get(dg)); m.transform(o.matrix_world); return m
mm=ev(bpy.data.objects[M]); T=BVHTree.FromPolygons([v.co[:] for v in mm.vertices],[p.vertices[:] for p in mm.polygons])
for o in b.objects[1:]:
    m=ev(o); bm=__import__('bmesh').new(); bm.from_mesh(m)
    bd=[v.co.copy() for v in bm.verts if v.is_boundary]
    H=collections.defaultdict(list)
    for c in bd:
        if c.x>-200: continue
        n=T.find_nearest(c)
        if n[0] is None or (mathutils.Vector((n[0].x,n[0].y))-mathutils.Vector((c.x,c.y))).length>3: continue
        H[int(c.y//50)*50].append(round(c.z-n[0].z,2))
    for k in sorted(H):
        d=sorted(H[k]); print('P235G',o.name[:14],'y',k,'n',len(d),'med',d[len(d)//2],'min',d[0],'max',d[-1],flush=True)
