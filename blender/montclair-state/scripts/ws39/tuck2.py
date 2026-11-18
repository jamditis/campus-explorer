import bpy,os
from mathutils import Vector
pad=bpy.data.objects['WS39_Kasser_steps_foot_landing_concrete_UNVERIFIED']
PZ=min((pad.matrix_world@v.co).z for v in pad.data.vertices if (pad.matrix_world@v.co).z>120)  # lower bound of top ~127.06
PZ=min(z for z in [(pad.matrix_world@v.co).z for v in pad.data.vertices] if z>127.0)
print('W39T pad top min',round(PZ,3))
for name in ('WS27_CollegeAve_carriageway_2020ortho','WS27_CollegeAve_curb_right_UNVERIFIED','WS27_CollegeAve_curb_left_UNVERIFIED'):
    o=bpy.data.objects[name]; m=o.matrix_world; mi=m.inverted(); c=0
    for v in o.data.vertices:
        p=m@v.co
        if -203.2<p.x<-198.3 and -98.2<p.y<-86.0 and p.z>PZ-0.08:
            v.co=mi@Vector((p.x,p.y,PZ-0.08)); c+=1
    o.data.update(); print('W39T tucked',name,c)
if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('W39T SAVED')
