import bpy, mathutils
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
for p in ((3,15.5,138.9),(6.3,14.0,139.0),(6.3,16.95,138.95)):
    for d in ((1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1)):
        r=sc.ray_cast(dg,mathutils.Vector(p),mathutils.Vector(d))
        print('PR',p,d,r[0] and round((r[1]-mathutils.Vector(p)).length,2), r[4].name if r[0] else None)
