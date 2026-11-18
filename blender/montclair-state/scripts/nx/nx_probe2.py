import bpy, mathutils
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
for y in (25.5,26.0,26.5,27.0,27.5):
  for d,src in (((1,0,0),(-17.5,y,139.0)),((0,-1,0),(-15.5,29.5,139.0))):
    r=sc.ray_cast(dg,mathutils.Vector(src),mathutils.Vector(d))
    print('HRAY',src,d,r[0],[round(c,2) for c in r[1]] if r[0] else None, r[4].name if r[0] else None)
  for x in (-16.5,-15.5,-14.75,-14.25,-13.75,-13.25):
    r=sc.ray_cast(dg,mathutils.Vector((x,y,142.9)),mathutils.Vector((0,0,-1)))
    print('DRAY',x,y,round(r[1].z,2) if r[0] else None, r[4].name if r[0] else None)
