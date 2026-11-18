import bpy
from mathutils import Vector
dg=bpy.context.evaluated_depsgraph_get()
def rz(o,x,y):
    e=o.evaluated_get(dg); oi=o.matrix_world.inverted()
    ok,hp,_,_=e.ray_cast(oi@Vector((x,y,200)),(oi.to_3x3()@Vector((0,0,-1))).normalized())
    return (o.matrix_world@hp).z if ok else None
R=bpy.data.objects['Roads_OSM'];T=bpy.data.objects['Terrain_LiDAR_DTM_1m']
rows=[]
for yi in range(-100,-48):
    y=yi*0.5; s=''
    for xi in range(-14,-3):
        x=xi*0.5; r=rz(R,x,y); t=rz(T,x,y)
        s+= '.' if r is None else ('#' if t is not None and t>r-0.005 else ('-' if t is not None and t>r-0.03 else 'o'))
    print('ROW %6.1f %s'%(y,s))
# also material slots of road faces there
