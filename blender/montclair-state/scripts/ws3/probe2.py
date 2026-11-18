import bpy
from mathutils import Vector
sc=bpy.context.scene
d=bpy.data.objects['COLE_add_forecourt_bu']
bb=[d.matrix_world@Vector(c) for c in d.bound_box]
x0=min(p.x for p in bb);x1=max(p.x for p in bb);y0=min(p.y for p in bb);y1=max(p.y for p in bb)
print('DISC',round(x0,1),round(x1,1),round(y0,1),round(y1,1),round(min(p.z for p in bb),2),round(max(p.z for p in bb),2))
m=d.data; print('DISCMESH',len(m.vertices),len(m.polygons),[s.material.name for s in d.material_slots], d.parent, [md.type for md in d.modifiers])
E=12
X0,X1,Y0,Y1=x0-E,x1+E,y0-E,y1+E
for o in sc.objects:
  if o.type!='MESH' or o.hide_render: continue
  if o.name.startswith(('Lamp_','Bench_')): continue
  bb=[o.matrix_world@Vector(c) for c in o.bound_box]
  if max(p.x for p in bb)<X0 or min(p.x for p in bb)>X1 or max(p.y for p in bb)<Y0 or min(p.y for p in bb)>Y1: continue
  me=o.data; mw=o.matrix_world
  n=0; zs=[]
  if len(me.vertices)<400000:
    for v in me.vertices:
      p=mw@v.co
      if X0<p.x<X1 and Y0<p.y<Y1: n+=1; zs.append(p.z)
  if n==0: continue
  print('OBJ',o.name,len(me.vertices),'in',n,'z',round(min(zs),2),round(max(zs),2),[s.material.name for s in o.material_slots if s.material][:4],[c.name for c in o.users_collection][:1],[md.type for md in o.modifiers][:3])
