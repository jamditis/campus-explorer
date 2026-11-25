# ws239 W53s part 2 (self-review fix): after f239a lowered M3b's edge + rings, the strips' own outer (free) edges, which
# ws236e tucked 5 mm under the OLD M3b surface, stood over the lowered M3b rings -> a dark lip line seen from the SW rail.
# Re-tuck: every PK/WS60/WS68 boundary vert whose vertical ray hits M3b within 1 m goes to min(z, M3b z - 5 mm).
import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
O=bpy.data.objects
M=O['M3b_north_LiDAR_DTM_1m_west_rail_corridor_UNVERIFIED_seam']
bm=bmesh.new(); bm.from_mesh(M.data); bm.transform(M.matrix_world); T=BVHTree.FromBMesh(bm); bm.free()
S=['PK_Feliciano_west_DTM_fill_UNVERIFIED','WS60_terrain_edge_apron_LiDAR_to_skirt']+[o.name for o in O if o.name.startswith('WS68_RHD_ground_northDTM')]
for n in S:
    o=O[n]; mw=o.matrix_world; iw=mw.inverted(); b=bmesh.new(); b.from_mesh(o.data); k=0; mx=0
    for v in b.verts:
        if not any(e.is_boundary for e in v.link_edges): continue
        w=mw@v.co; h=T.ray_cast(w+Vector((0,0,1.0)),Vector((0,0,-1)),2.0)
        if h[0] is None: continue
        t=h[0].z-0.005
        if w.z>t: mx=max(mx,w.z-t); w.z=t; v.co=iw@w; k+=1
    b.to_mesh(o.data); b.free(); o.data.update()
    print('F239B',n[:30],'retucked',k,'max drop %.3f'%mx,flush=True)
