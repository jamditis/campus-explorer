# qc: render-time only (never saved). Box had only ~2.9 GB available (host-side usage); pw chain hit 1.95 GB at mesh sync and the
# guard fired. Per single camera: hide_render every object whose bounding box lies farther than RAD m from the camera
# (except very large terrain/ortho drapes, max dim > LARGE), then the usual pw/ot chain. Run ONE camera per process.
import bpy, os
from mathutils import Vector
cam=bpy.data.objects[os.environ['CAMS'].split(',')[0]]; cl=cam.matrix_world.translation
R=float(os.environ.get('RAD','450')); LG=float(os.environ.get('LARGE','300')); nh=0
for o in bpy.context.scene.objects:
    if o.hide_render or o.type not in ('MESH','CURVES','POINTCLOUD','CURVE','FONT') or max(o.dimensions)>LG: continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    lo=Vector((min(p.x for p in bb),min(p.y for p in bb),min(p.z for p in bb))); hi=Vector((max(p.x for p in bb),max(p.y for p in bb),max(p.z for p in bb)))
    q=Vector((min(max(cl.x,lo.x),hi.x),min(max(cl.y,lo.y),hi.y),min(max(cl.z,lo.z),hi.z)))
    if (q-cl).length>R: o.hide_render=True; nh+=1
print('QD_RADCULL',cam.name,R,nh)
exec(open('scripts/qe/pw_render_lowmem.py').read())
