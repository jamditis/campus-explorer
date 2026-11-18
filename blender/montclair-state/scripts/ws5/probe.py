import bpy
from mathutils import Vector
for o in bpy.data.objects:
  if o.type not in ('MESH','CURVE'): continue
  cs=[o.matrix_world@Vector(c) for c in o.bound_box]
  lo=[min(c[i] for c in cs) for i in range(3)]; hi=[max(c[i] for c in cs) for i in range(3)]
  if hi[0]>-135 and lo[0]<-80 and hi[1]>-100 and lo[1]<-25 and (hi[0]-lo[0])<120:
    vis=not o.hide_render and all(not c.hide_render for c in o.users_collection)
    print('O',o.name,'|',[round(x,1) for x in lo],[round(x,1) for x in hi],'vis' if vis else 'HID',[m.name for m in o.data.materials][:4] if hasattr(o.data,'materials') else '',[c.name for c in o.users_collection][:2])
for c in bpy.data.objects:
  if c.type=='CAMERA' and ('ole' in c.name or 'COLE' in c.name): print('CAM',c.name,[round(v,1) for v in c.location],[round(v,2) for v in c.rotation_euler],c.data.lens)
