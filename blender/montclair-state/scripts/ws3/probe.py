import bpy
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view as w2c
sc=bpy.context.scene
cam=bpy.data.objects['CAM_oblique_cole_hall_nnw_br']
print('CAM',[round(v,2) for v in cam.matrix_world.translation],cam.data.lens)
# disc region in image coords (x 0..1 left->right, y 0..1 bottom->top)
X0,X1,Y0,Y1=0.08,0.50,0.0,0.45
rows=[]
for o in sc.objects:
  if o.type!='MESH' or o.hide_render: continue
  bb=[o.matrix_world@Vector(c) for c in o.bound_box]
  dz=max(p.z for p in bb)-min(p.z for p in bb)
  dx=max(p.x for p in bb)-min(p.x for p in bb); dy=max(p.y for p in bb)-min(p.y for p in bb)
  if max(dx,dy)>400: continue
  pr=[w2c(sc,cam,p) for p in bb]
  if any(p.z<=0 for p in pr): continue
  cx=sum(p.x for p in pr)/8; cy=sum(p.y for p in pr)/8
  if X0<cx<X1 and Y0<cy<Y1:
    mats=[s.material.name for s in o.material_slots if s.material][:3]
    rows.append((cy,o.name,round(cx,2),round(cy,2),round(dx,1),round(dy,1),round(dz,2),len(o.data.polygons),mats,[c.name for c in o.users_collection][:1],[round(v,1) for v in o.matrix_world.translation]))
rows.sort()
for r in rows: print('OBJ',*r[1:])
