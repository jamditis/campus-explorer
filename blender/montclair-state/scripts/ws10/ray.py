import bpy
from mathutils import Vector
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
for y in range(-64,-36,2):
  row=[]
  for x in range(-84,-42,3):
    r=sc.ray_cast(dg,Vector((x,y,170)),Vector((0,0,-1)))
    row.append((x,r[4].name[:22] if r[0] else '-', round(r[1].z,2) if r[0] else 0))
  print('ROW',y,row)
