import bpy, mathutils
from mathutils.bvhtree import BVHTree
X0,X1,Y0,Y1=-125,-90,290,345
for o in bpy.data.objects:
    if o.type!='MESH': continue
    bb=[o.matrix_world@mathutils.Vector(c) for c in o.bound_box]
    xs=[v.x for v in bb]; ys=[v.y for v in bb]; zs=[v.z for v in bb]
    if max(xs)>X0 and min(xs)<X1 and max(ys)>Y0 and min(ys)<Y1 and (max(xs)-min(xs))<3000:
        m=[s.material.name for s in o.material_slots if s.material][:3]
        print(o.name,'|',o.users_collection[0].name,'| x%.0f..%.0f y%.0f..%.0f z%.1f..%.1f'%(min(xs),max(xs),min(ys),max(ys),min(zs),max(zs)),len(o.data.polygons),m,'hide' if o.hide_render else '')
# ground height samples via terrain
dg=bpy.context.evaluated_depsgraph_get()
for y in (300,310,320,330):
  row=[]
  for x in (-120,-112,-106,-100,-96,-94):
    hit=bpy.context.scene.ray_cast(dg,(x,y,200),(0,0,-1))
    row.append('%s:%.2f'%(hit[4].name[:18] if hit[0] else '-',hit[1].z if hit[0] else 0))
  print(y,row)
