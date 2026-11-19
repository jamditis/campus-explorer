# ws222g: the ws222f top/bottom faces of the WS72 landing next to the new curb-back edge became non-planar n-gons (11+ verts),
# which rendered as a wavy crease above the curb arc. Triangulate those n-gons (beauty) so the slab top shades as flat facets.
import bpy, bmesh
L=bpy.data.objects['WS72_Kasser_SW_RHD_core_sidewalk_landing_UNVERIFIED_width']
bm=bmesh.new(); bm.from_mesh(L.data)
ng=[f for f in bm.faces if len(f.verts)>4]
print('F222G ngons',[len(f.verts) for f in ng],flush=True)
bmesh.ops.triangulate(bm,faces=ng,quad_method='BEAUTY',ngon_method='BEAUTY')
bm.to_mesh(L.data); bm.free(); L.data.update(); print('F222G polys',len(L.data.polygons),flush=True)
