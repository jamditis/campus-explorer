# ws242: the f242b/f242d flaps come out of extrude_edge_only with their winding opposite to the tile (normal pointing down
# -> pale, sky-reflecting shading in the test render). Flip every face of M3a/M3b whose normal points down (terrain tiles
# are height fields; before ws242 both had 0 down-facing faces).
import bpy, bmesh
for o in [x for x in bpy.data.objects if x.name.startswith(('M3a_north_LiDAR_DTM_1m','M3b_north_LiDAR_DTM_1m'))]:
    bm=bmesh.new(); bm.from_mesh(o.data); bm.normal_update()
    F=[f for f in bm.faces if f.normal.z<0]
    if F: bmesh.ops.reverse_faces(bm,faces=F)
    bm.to_mesh(o.data); o.data.update(); bm.free()
    print('F242E',o.name[:12],'flipped',len(F),flush=True)
