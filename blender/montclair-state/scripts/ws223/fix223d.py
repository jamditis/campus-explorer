# ws223d: the WS72 landing top at the W39 curb-return corner was built from a chord face (f165: v150-v266-v152) whose
# edge v150->v266 cuts straight across the curb top (up to ~3-13 cm proud of the curb back), plus a fan of 6 downward
# faces (f90, f166-f170) filling ring<->chord ON TOP of the curb. That double, unsupported sheet = the white 'fold' over
# the curb in the S eye view. Those 7 faces are removed and the top polygon v150 -> v260..v266 -> v152 is re-filled by
# ear-clipping (tessellate_polygon) so the slab top ends exactly at the side-face ring (= 1 cm inside the curb back),
# normals up. No vertex moves.
import bpy, bmesh
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
o=bpy.data.objects['WS72_Kasser_SW_RHD_core_sidewalk_landing_UNVERIFIED_width']; M=o.matrix_world
bm=bmesh.new(); bm.from_mesh(o.data); bm.verts.ensure_lookup_table()
ring=[150]+list(range(260,267))+[152]
RS=set(ring)
kill=[f for f in bm.faces if set(v.index for v in f.verts)<=RS]
print('F223D removing',[f.index for f in kill],flush=True)
assert len(kill)==7,len(kill)
for f in kill: bm.faces.remove(f)
V=[bm.verts[i] for i in ring]
W=[M@v.co for v in V]
tris=tessellate_polygon([[Vector((w.x,w.y,0)) for w in W]])
n=0
for t in tris:
    f=bm.faces.new([V[i] for i in t]); f.normal_update()
    if (M.to_3x3()@f.normal).z<0: f.normal_flip()
    n+=1
bm.normal_update()
# report max overhang: ring vs chord no longer used; print area check
tot=sum(f.calc_area() for f in bm.faces if set(v.index for v in f.verts)<=RS)
print('F223D new faces',n,'area %.3f'%tot,flush=True)
bm.to_mesh(o.data); bm.free(); o.data.update()
