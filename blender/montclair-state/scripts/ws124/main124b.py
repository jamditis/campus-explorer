# ws124b: replace the straight S strip with a slab that paves the whole recess floor to the LiDAR-massing walls:
# S-wing N face is skewed (y -201.23 at x -215.71 -> -202.71 at x -209.6) and a 1.5 x 2 m alcove opens S of the door pier (x -209.6..-207.6, y -201.25..-202.98).
import bpy, bmesh, os
o=bpy.data.objects['WS124_Chapin_W_landing_S_strip_to_S_wing_face_UNIFY30']; mats=list(o.data.materials)
bm=bmesh.new(); Z0,Z1=124.52,124.768
P=[(-213.40,-201.30),(-207.45,-201.30),(-207.45,-203.15),(-209.75,-203.15),(-213.40,-202.02)]
vs=[bm.verts.new((x,y,Z0)) for x,y in P]; f=bm.faces.new(vs)
if f.normal.z>0: f.normal_flip()
r=bmesh.ops.extrude_face_region(bm,geom=[f]); top=[e for e in r['geom'] if isinstance(e,bmesh.types.BMVert)]
for v in top: v.co.z=Z1
bm.normal_update(); bmesh.ops.recalc_face_normals(bm,faces=bm.faces[:])
o.data.clear_geometry(); bm.to_mesh(o.data); bm.free(); o.data.update()
o.name='WS124_Chapin_W_landing_S_recess_floor_to_LiDAR_walls_UNIFY30'; o.data.name=o.name
print('M124b faces',len(o.data.polygons))
bpy.ops.wm.save_mainfile(); print('M124b SAVED')
