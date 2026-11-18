import bpy
from mathutils import Vector
wo=bpy.data.objects['Schmitt Hall walls']; inv=wo.matrix_world.inverted()
es=[o for o in bpy.data.objects if o.name.startswith('SCH_win_')]
ok=bad=0; badl=[]
for e in es:
    M=e.matrix_world; Y=Vector((M[0][1],M[1][1],0)).normalized(); X=Vector((M[0][0],M[1][0],0)).normalized()
    p=M.translation+Vector((0,0,0.9))+Y*1.0
    h,l,n,i=wo.ray_cast(inv@p, (inv.to_3x3()@(-Y)).normalized(), distance=2.0)
    if h: bad+=1; badl.append(e.name)
    else: ok+=1
print('through-hole',ok,'blocked',bad,badl[:20])
me=wo.data; print('faces',len(me.polygons),'max verts/face',max(len(f.vertices) for f in me.polygons))
