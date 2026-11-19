# ws223e: WS72 landing quad f84 (v140,v150,v152,v142) is a long non-planar sliver (2.1 m x ~0.1-0.5 m) along the start of
# the W39 return; it was split along its long diagonal at render time, leaving a crease where the landing meets the arc.
# Split it explicitly along the short diagonal v150-v142 so both triangles follow the edge grade. No vertex moves.
import bpy, bmesh
o=bpy.data.objects['WS72_Kasser_SW_RHD_core_sidewalk_landing_UNVERIFIED_width']; M=o.matrix_world
bm=bmesh.new(); bm.from_mesh(o.data); bm.verts.ensure_lookup_table()
f=[f for f in bm.faces if set(v.index for v in f.verts)=={140,150,152,142}]; assert len(f)==1
r=bmesh.utils.face_split(f[0],bm.verts[150],bm.verts[142])
bm.normal_update()
for g in bm.faces:
    if set(v.index for v in g.verts)<= {140,150,152,142}:
        n=(M.to_3x3()@g.normal)
        if n.z<0: g.normal_flip()
        print('F223E face',[v.index for v in g.verts],'n (%.2f,%.2f,%.2f)'%tuple((M.to_3x3()@g.normal).normalized()),flush=True)
bm.to_mesh(o.data); bm.free(); o.data.update()
