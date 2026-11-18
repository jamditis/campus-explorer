import bpy
from mathutils import Vector
O=bpy.data.objects; dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
s=O['QS_footway_546643369_UNVERIFIED']; vs=[s.matrix_world@v.co for v in s.data.vertices]
print('BB',min(v.x for v in vs),max(v.x for v in vs),min(v.y for v in vs),max(v.y for v in vs))
top=sorted(vs,key=lambda v:-v.y)[:6]; print('NORTH',[tuple(round(c,2) for c in v) for v in top])
yN=max(v.y for v in vs)
for y in [yN-1,yN-0.5,yN,yN+0.25,yN+0.5,yN+1,yN+2]:
  row=[]
  for x in [v.x for v in top[:1]][0]+__import__('numpy').arange(-3,3.1,0.5):
    r=sc.ray_cast(dg,Vector((x,y,200)),Vector((0,0,-1)))
    row.append((round(x,1),r[4].name[:14] if r[0] else None,round(r[1].z,2) if r[0] else None))
  print('ROW',round(y,2),row)
