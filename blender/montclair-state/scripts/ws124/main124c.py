import bpy
ff=next(o for o in bpy.data.objects if o.name.startswith('WS113_terrain_fan_fill')); fm=ff.matrix_world; inv=fm.inverted(); n=0
for v in ff.data.vertices:
    w=fm@v.co
    if -210.1<w.x<-206.9 and -203.6<w.y<-201.6 and w.z>124.70: w.z=124.70; v.co=inv@w; n+=1
ff.data.update(); print('M124c fanfill lowered',n)
bpy.ops.wm.save_mainfile(); print('M124c SAVED')
