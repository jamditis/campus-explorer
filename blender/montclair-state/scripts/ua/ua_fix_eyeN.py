import bpy, os
from mathutils import Vector, bvhtree
SAVE = os.environ.get('SAVE') == '1'

o = bpy.data.objects.get('Context_skirt_3DEP_ortho_4km')
deps = bpy.context.evaluated_depsgraph_get()
eo = o.evaluated_get(deps)
mesh = eo.to_mesh()
mesh.transform(o.matrix_world)
bvh = bvhtree.BVHTree.FromPolygons([v.co.copy() for v in mesh.vertices],[p.vertices for p in mesh.polygons])
eo.to_mesh_clear()

def gz(x,y):
    hit = bvh.ray_cast(Vector((x,y,300)), Vector((0,0,-1)))
    return hit[0].z if hit and hit[0] is not None else None

road = bpy.data.objects.get('UA_NormalAve_CR618_583841725_727_729_UNVERIFIED')
bb = [road.matrix_world @ Vector(c) for c in road.bound_box]
rmid = Vector(((min(v.x for v in bb)+max(v.x for v in bb))/2,
               (min(v.y for v in bb)+max(v.y for v in bb))/2,
               (min(v.z for v in bb)+max(v.z for v in bb))/2))

# Stand ~22 m north of ribbon mid, look steeply down onto road surface
sx, sy = rmid.x + 5, rmid.y + 22
zg = gz(sx, sy) or (rmid.z + 4)
tz = gz(rmid.x, rmid.y) or rmid.z
cam = bpy.data.objects.get('UA_CAM_eye_NormalAve_from_N')
cam.location = Vector((sx, sy, zg + 5.5))
target = Vector((rmid.x + 15, rmid.y - 8, tz + 0.3))
cam.rotation_euler = (target - cam.location).to_track_quat('-Z', 'Y').to_euler()
cam.data.lens = 28
cam.data.clip_start = 0.05
print('eyeN', tuple(round(x,2) for x in cam.location), '->', tuple(round(x,2) for x in target), 'stand_z', zg, 'road_z', tz)
if SAVE:
    bpy.ops.wm.save_mainfile(); print('SAVED', len(bpy.data.objects))
