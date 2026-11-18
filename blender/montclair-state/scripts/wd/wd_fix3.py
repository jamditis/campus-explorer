import bpy, os
from mathutils import Vector
e=Vector((0.9444,-0.3291,0)).normalized(); nrm=Vector((-e.y,e.x,0)); M=Vector((226.825,413.425,0)); zL=132.45
def W(s,l,z=0): return Vector((M.x+e.x*s+nrm.x*l, M.y+e.y*s+nrm.y*l, z))
o=bpy.data.objects['WD_CAM_closeup_Bohn_N_steps']
loc=W(-5,5,134.8+2.2); tgt=W(-0.5,0,zL+0.2)
o.location=loc; o.rotation_euler=(tgt-loc).to_track_quat('-Z','Y').to_euler(); o.data.lens=22
print('CAM',[round(x,1) for x in loc])
if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')
