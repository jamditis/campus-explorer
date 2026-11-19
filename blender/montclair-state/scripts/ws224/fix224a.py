# ws224a (W45b): the NE-eye 'V-notch' at the Kasser landing / W39 curb-return corner. The WS220 curb BACK arc
# (rings k18..k29) coincides with the landing ring v150 -> v260..v266, so the slab must end on that arc. But the ws223d
# fan (ring + v152, ear-clipped) and the ws223f fill (chord v150 -> v152) both covered the area SOUTH-EAST of the arc:
# two stacked landing sheets lying 1-4 cm over the curb top and up to ~10 cm past the curb FRONT, hanging ~21 cm over
# the gutter (= the vertical slab face / notch in the NE view). Both fills are removed and the single simple polygon
# v130 -> v140 -> v150 -> v260..v266 -> v152 -> v142 -> v132 is re-filled by ear-clipping (slab ends on the curb back),
# normals up. No vertex moves (topology only).
import bpy, bmesh
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
o=bpy.data.objects['WS72_Kasser_SW_RHD_core_sidewalk_landing_UNVERIFIED_width']; M=o.matrix_world
bm=bmesh.new(); bm.from_mesh(o.data); bm.verts.ensure_lookup_table()
poly=[130,140,150]+list(range(260,267))+[152,142,132]; PS=set(poly)
kill=[f for f in bm.faces if set(v.index for v in f.verts)<=PS]
print('F224A removing',len(kill),[[v.index for v in f.verts] for f in kill],flush=True)
assert 8<=len(kill)<=14,len(kill)
a0=sum(f.calc_area() for f in kill)
for f in kill: bm.faces.remove(f)
V=[bm.verts[i] for i in poly]; W=[M@v.co for v in V]
a1=0
for t in tessellate_polygon([[Vector((w.x,w.y,0)) for w in W]]):
    f=bm.faces.new([V[i] for i in t]); f.normal_update()
    if (M.to_3x3()@f.normal).z<0: f.normal_flip()
    a1+=f.calc_area()
print('F224A area removed %.3f m2 -> refilled %.3f m2'%(a0,a1),flush=True)
bm.normal_update(); bm.to_mesh(o.data); bm.free(); o.data.update()
