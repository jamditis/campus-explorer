# ot cams: aerial over the north strip (context skirt fix) + close-up of the CELS base-course corner. REVERT=1 removes them.
import bpy, os, sys
from mathutils import Vector
REV=os.environ.get('REVERT')=='1'; SAVE='--save' in sys.argv; CN='OT_cams_20261031ot'
c=bpy.data.collections.get(CN)
if c:
    for o in list(c.objects):
        d=o.data; bpy.data.objects.remove(o); bpy.data.cameras.remove(d)
    bpy.data.collections.remove(c)
if REV:
    print('REVERTED')
    if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
    raise SystemExit(0)
scn=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
col=bpy.data.collections.new(CN); scn.collection.children.link(col)
def cam(n,loc,tgt,lens):
    d=bpy.data.cameras.new(n); d.lens=lens; d.clip_end=6000; o=bpy.data.objects.new(n,d); col.objects.link(o)
    o.location=loc; o.rotation_euler=(Vector(tgt)-Vector(loc)).to_track_quat('-Z','Y').to_euler(); return o
cam('OT_CAM_aerial_north_strip_CELS_Calcia',(5,110,215),(5,228,132),24)
# close-up: ray from the CELS eye cam through the base-course pilaster corner (px 130,255 of 768x432)
ec=bpy.data.objects['OR_CAM_eye_CELS_skirt_windows_base_course']; fr=[ec.matrix_world@v for v in ec.data.view_frame(scene=scn)]; o=ec.matrix_world.translation
tl,tr,br,bl=fr[3],fr[0],fr[1],fr[2]; p=bl+(br-bl)*(130/768)+(tl-bl)*(1-255/432)
h=scn.ray_cast(dg,o,(p-o).normalized(),distance=200); hit=h[1]; print('CORNER',h[4].name,[round(x,2) for x in hit])
dv=(o-hit); dv.z=0; dv.normalize()
cam('OT_CAM_closeup_CELS_base_course_corner',hit+dv*5.0+Vector((0,0,1.1)),hit+Vector((0,0,0.15)),35)
print('CAMS OK')
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
