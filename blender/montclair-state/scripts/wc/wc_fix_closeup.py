# Reposition WC closeup onto mid-facade of NW lower block (first cam was at wall-foot / grass).
import bpy, json, math
from mathutils import Vector
ROOT='/workspace/nj-scenes/montclair-state'
d=json.load(open(ROOT+'/data/wc/apply.json'))
O=Vector((d['origin'][0], d['origin'][1], 0))
U=Vector((d['U'][0], d['U'][1], 0))
N=Vector((d['N'][0], d['N'][1], 0))
tm=d['frame_tm']
cam=bpy.data.objects['WC_CAM_closeup_Bohn_NW_lower_W_piers']
# stand ~18 m out, z mid-base (~128.5), look at mid-grid pier lines around z 128
t,n,z = tm, 18.0, 128.5
tt,tn,tz = tm, 0.0, 128.0
p = O + U*t + N*n; q = O + U*tt + N*tn
cam.location=(p.x, p.y, z)
dvec=Vector((q.x-p.x, q.y-p.y, tz-z))
cam.rotation_euler=(math.pi/2+math.atan2(dvec.z, math.hypot(dvec.x,dvec.y)), 0,
                    math.atan2(dvec.y,dvec.x)-math.pi/2)
cam.data.lens=32
print('CLOSEUP', [round(a,2) for a in cam.location], 'lens', cam.data.lens)
bpy.ops.wm.save_mainfile(); print('SAVED', len(bpy.data.objects))
