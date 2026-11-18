import bpy
from mathutils import Vector
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
r=bpy.data.objects['Calcia Hall roof (LiDAR)']; w=bpy.data.objects['Calcia Hall walls']; me=w.data
for y in [186+i for i in range(0,14)]+[198.0,198.2]:
    hit,loc,nor,idx,ob,mx=sc.ray_cast(dg,Vector((-106.4,y,200)),Vector((0,0,-1)))
    # wall top near x -106.9 at this y
    tops=[(w.matrix_world@v.co).z for v in me.vertices if abs((w.matrix_world@v.co).y-y)<0.6 and (w.matrix_world@v.co).x<-106.5]
    print('GAP y',y,'hit',ob and ob.name,round(loc.z,2),'walltop',round(max(tops),2) if tops else None)
