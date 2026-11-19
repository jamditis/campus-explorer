# ws223f: ROOT CAUSE of the 'fold' at the W39 return start. WS72 landing top quads f78 (v130,v140,v142,v132) and f84
# (v140,v150,v152,v142) overlap: v150 (-248.93,-53.62) lies WEST of the shared edge v140->v142, so f84 is a folded quad
# lying on top of f78 (two top sheets 2-4 cm apart = z-fight + white crease over the curb in the S eye view). Both are
# removed and the simple polygon v130 -> v140 -> v150 -> v152 -> v142 -> v132 is re-filled by ear-clipping, normals up.
# No vertex moves.
import bpy, bmesh
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
o=bpy.data.objects['WS72_Kasser_SW_RHD_core_sidewalk_landing_UNVERIFIED_width']; M=o.matrix_world
bm=bmesh.new(); bm.from_mesh(o.data); bm.verts.ensure_lookup_table()
poly=[130,140,150,152,142,132]; PS=set(poly)
kill=[f for f in bm.faces if set(v.index for v in f.verts)<=PS]
print('F223F removing',[[v.index for v in f.verts] for f in kill],flush=True)
assert len(kill) in (2,3),len(kill)
for f in kill: bm.faces.remove(f)
V=[bm.verts[i] for i in poly]; W=[M@v.co for v in V]
for t in tessellate_polygon([[Vector((w.x,w.y,0)) for w in W]]):
    f=bm.faces.new([V[i] for i in t]); f.normal_update()
    if (M.to_3x3()@f.normal).z<0: f.normal_flip()
    print('F223F tri',[poly[i] for i in t],'nz %.2f'%(M.to_3x3()@f.normal).normalized().z,flush=True)
bm.normal_update(); bm.to_mesh(o.data); bm.free(); o.data.update()
