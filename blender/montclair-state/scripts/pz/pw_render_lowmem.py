# pw: render-time only. Box had ~2.9 GB available (host-side usage), the ot chain peaked ~3.2 GB. Camera-cull every object
# (not just grass) except very large ones (terrain/ortho drapes, max bbox dim > LARGE m), so off-frustum objects are not synced.
import bpy, os
L=float(os.environ.get('LARGE','300')); n=0
for o in bpy.context.scene.objects:
    if o.type in ('MESH','CURVES','POINTCLOUD','CURVE','FONT') and max(o.dimensions)<L: o.cycles.use_camera_cull=True; n+=1
print('PW_CULL_ALL',n)
exec(open('scripts/ot/ot_render_lowmem.py').read())
