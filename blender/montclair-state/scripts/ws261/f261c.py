# ws261c->d: fill a ~0.2 x 0.3 m evaluated pinhole (Context_ground_beyond_data showing) at the Chapin W wall foot, x -216.5..-216.3,
# y -203.6..-203.3 (probe261e/g), between Terrain_LiDAR_DTM_1m (122.61), a WS12x wall piece and the WS12x paving (122.67).
# Small flat quad 0.7 x 0.7 m at 122.60 (1 cm under the neighbouring terrain) with the WS113 fan-fill lawn material; it tucks under
# the neighbours everywhere except the hole.
import bpy
TAG='F261C'; SN='WS261_UNIFY32_Chapin_W_wall_foot_pinhole_fill'
if SN in bpy.data.objects: raise SystemExit('already')
src=[x for x in bpy.data.objects if x.name.startswith('WS113_terrain_fan_fill_DTM1m')][0]
x0,x1,y0,y1,z=-216.75,-216.05,-203.80,-203.10,122.60
me=bpy.data.meshes.new(SN); me.from_pydata([(x0,y0,z),(x1,y0,z),(x1,y1,z),(x0,y1,z)],[],[(0,1,2,3)])
# material: the nearest WS113 face's material (by centroid); if it is the ortho-UV one, use the procedural lawn instead
import mathutils
c=mathutils.Vector(((x0+x1)/2,(y0+y1)/2,z)); W=src.matrix_world
best=min(src.data.polygons,key=lambda p:((W@p.center).xy-c.xy).length)
mat=src.data.materials[best.material_index]
if mat.name=='Ground_ortho_grass': mat=bpy.data.materials.get('COLE_lawn_post2020_bs') or mat
me.materials.append(mat)
ob=bpy.data.objects.new(SN,me); src.users_collection[0].objects.link(ob)
print(TAG,'made',SN,'mat',[m.name for m in me.materials],flush=True)
