import bpy, bmesh
from mathutils import Vector as V
o=bpy.data.objects['UV_Freeman_N_entrance_curtain_doors_canopy_UNVERIFIED']; mw=o.matrix_world
bm=bmesh.new(); bm.from_mesh(o.data)
kill=[f for f in bm.faces if 131.1<(mw@f.calc_center_median()).z<131.8 and (mw@f.calc_center_median()).y>-169.6 and any(abs((mw@f.calc_center_median()).x-x)<0.05 for x in (-85.925,-88.285))]
print('KILL',len(kill))
bmesh.ops.delete(bm,geom=kill,context='FACES'); bm.to_mesh(o.data); bm.free()
bpy.ops.wm.save_as_mainfile(filepath='/workspace/nj-scenes/montclair-state/montclair_state.blend')
