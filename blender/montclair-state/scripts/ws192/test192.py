import bpy, numpy as np
from mathutils import Vector
S='/workspace/nj-scenes/montclair-state/scripts/'
exec(open(S+'ws192/fix192.py').read())
o=bpy.data.objects['WS192_Lot3_S_strip_E_end_lawn_fillet_LiDAR_rise_UNVERIFIED']
V=np.array([tuple(v.co) for v in o.data.vertices]); print('T192 bbox',V.min(0).round(3),V.max(0).round(3))
dg=bpy.context.evaluated_depsgraph_get()
for y in [-235.2,-235.6,-236.0,-236.4]:
  s=[]
  for x in np.arange(-299.3,-297.8,0.15):
    r=bpy.context.scene.ray_cast(dg,Vector((x,y,300)),Vector((0,0,-1)))
    s.append('%s:%.3f'%(r[4].name[:6] if r[0] else '-',r[1].z if r[0] else 0))
  print('T192 y',y,' '.join(s))
