# Closeup above NW grade (~136) aimed at visible L1 + top-of-base eggcrate junction.
import bpy, json, math
from mathutils import Vector
ROOT='/workspace/nj-scenes/montclair-state'
d=json.load(open(ROOT+'/data/wc/apply.json'))
O=Vector((d['origin'][0], d['origin'][1], 0))
U=Vector((d['U'][0], d['U'][1], 0))
N=Vector((d['N'][0], d['N'][1], 0))
tm=d['frame_tm']
# station from cam_search: dt=0, n=16, z=138 (above_g 2.08) — but aim at L1 mid (~137.8)
# pull a bit further for pier rhythm: n=20, z=138.5, look at tm, n=0, z=137.5
t,n,z = tm, 20.0, 138.5
tt,tn,tz = tm, 0.0, 137.5
p = O + U*t + N*n; q = O + U*tt + N*tn
cam=bpy.data.objects['WC_CAM_closeup_Bohn_NW_lower_W_piers']
cam.location=(p.x, p.y, z)
dvec=Vector((q.x-p.x, q.y-p.y, tz-z))
cam.rotation_euler=(math.pi/2+math.atan2(dvec.z, math.hypot(dvec.x,dvec.y)), 0,
                    math.atan2(dvec.y,dvec.x)-math.pi/2)
cam.data.lens=35
# quick ray check
dg=bpy.context.evaluated_depsgraph_get()
direction=(q+Vector((0,0,tz))-Vector((0,0,0)))  # unused
direction = Vector((q.x-p.x, q.y-p.y, tz-z)).normalized()
hit,loc,_,_,obj,_=bpy.context.scene.ray_cast(dg, Vector(cam.location), direction, distance=40)
print('CLOSEUP2', [round(a,2) for a in cam.location], 'lens', cam.data.lens,
      'hit', obj.name[:40] if obj else None, [round(a,2) for a in loc] if hit else None)
bpy.ops.wm.save_mainfile(); print('SAVED', len(bpy.data.objects))
