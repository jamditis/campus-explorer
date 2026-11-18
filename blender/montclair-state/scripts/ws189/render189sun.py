# ws189: sun-shadow test — rotate the GOLDEN sun lamp + sky sun by SUNDEG (deg, about Z) at render_pre, then run render185
import bpy, os, math
from bpy.app.handlers import persistent
D=math.radians(float(os.environ.get('SUNDEG','20'))); _done=[]
@persistent
def _rot(*a):
    if _done: return
    o=bpy.data.objects.get('WP2_Sun_GOLDEN')
    if o: o.rotation_euler.z+=D; print('SUN189 lamp z',round(o.rotation_euler.z,3),flush=True)
    w=bpy.context.scene.world
    for nd in w.node_tree.nodes:
        if nd.type=='TEX_SKY': nd.sun_rotation+=D; print('SUN189 sky rot',round(nd.sun_rotation,3),'sun_disc',nd.sun_disc,flush=True)
    _done.append(1)
bpy.app.handlers.render_pre.append(_rot)
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws185/render185.py').read())
