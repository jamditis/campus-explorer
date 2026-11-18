import bpy, bmesh
from mathutils import Vector
X0,X1,Y0,Y1=-85,-30,-75,-30
for o in bpy.data.objects:
  if o.type!='MESH' or o.hide_render: continue
  bb=[o.matrix_world@Vector(c) for c in o.bound_box]
  xs=[v.x for v in bb]; ys=[v.y for v in bb]
  if max(xs)<X0 or min(xs)>X1 or max(ys)<Y0 or min(ys)>Y1: continue
  if max(xs)-min(xs)>400: continue
  n=len(o.data.polygons)
  print('OBJ',o.name,n,[round(min(xs),1),round(max(xs),1),round(min(ys),1),round(max(ys),1),round(min(v.z for v in bb),1),round(max(v.z for v in bb),1)],[m.name for m in o.data.materials if m][:3])
