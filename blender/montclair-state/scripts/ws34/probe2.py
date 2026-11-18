import bpy
from mathutils import Vector
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
ter=bpy.data.objects['Terrain_LiDAR_DTM_1m']; te=ter.evaluated_get(dg); mi=ter.matrix_world.inverted()
def tz(x,y):
    ok,hp,_,_=te.ray_cast(mi@Vector((x,y,300)),Vector((0,0,-1)))
    return (ter.matrix_world@hp).z if ok else None
from collections import Counter
cnt=Counter()
for yi in range(-104,-76,2):
  row=[]
  for xi in range(-216,-186,2):
    ok,loc,n,i,o,m=sc.ray_cast(dg,Vector((xi,yi,200)),Vector((0,0,-1)))
    t=tz(xi,yi)
    nm=o.name[:10] if ok else '-'
    cnt[o.name if ok else '-']+=1
    d=(loc.z-t) if (ok and t) else 0
    row.append('%s:%+.1f'%(nm[:6],d))
  print('ROW',yi,' '.join(row))
print('CNT',cnt.most_common(15))
