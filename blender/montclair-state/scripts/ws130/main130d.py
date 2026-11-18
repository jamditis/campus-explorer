# ws130 self-review fix 3: Roads_OSM residue faces sat 6-7 cm ABOVE the WS130 drive at the hatch S end (x -196.6, y -229.5..-231,
# raycast); the whole OSM service-road leg there is superseded by designed asphalt -> retire every Roads_OSM face with its centroid
# in x -201.5..-180, y -256..-210.
import bpy, bmesh, os
ro=bpy.data.objects['Roads_OSM']; rw=ro.matrix_world
bm=bmesh.new(); bm.from_mesh(ro.data)
k=[f for f in bm.faces if (lambda c:-201.5<c.x<-180 and -256<c.y<-210)(rw@f.calc_center_median())]
bmesh.ops.delete(bm,geom=k,context='FACES'); bm.to_mesh(ro.data); bm.free(); ro.data.update(); print('M130d Roads_OSM faces retired',len(k))
if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('M130d SAVED')
