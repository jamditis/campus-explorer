import bpy
from mathutils import Vector
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
for (x,y) in ((22,236),(30,262),(35,275),(25,285),(40,250),(150,232),(135,245),(130,255),(140,262),(125,265),(84,222),(45,225)):
    ok,loc,n,i,ob,m=sc.ray_cast(dg,Vector((x,y,300)),Vector((0,0,-1)))
    print('PROBE',(x,y),ok and round(loc.z,2),ob.name if ok else None)
