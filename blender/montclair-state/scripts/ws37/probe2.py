import bpy
from mathutils import Vector
dg=bpy.context.evaluated_depsgraph_get()
def mk(n):
    o=bpy.data.objects[n]; e=o.evaluated_get(dg); mi=o.matrix_world.inverted()
    def f(x,y):
        ok,hp,_,_=e.ray_cast(mi@Vector((x,y,400)),(mi.to_3x3()@Vector((0,0,-1))).normalized())
        return (o.matrix_world@hp).z if ok else None
    return f
C=mk('WS27_CollegeAve_carriageway_2020ortho'); T=mk('Terrain_LiDAR_DTM_1m')
cands=[o.name for o in bpy.data.objects if o.type=='MESH' and ('CollegeAve' in o.name or o.name=='Roads_OSM')]
print('cands',cands)
for y in range(-88,-114,-2):
    row=''
    for x in range(-222,-192,1):
        c=C(x,y); t=T(x,y)
        if c is None: row+='.'
        elif t is None: row+='?'
        else:
            d=c-t; row+= '#' if d<0.0 else ('x' if d<0.03 else ('o' if d<0.06 else '-'))
    print(y,row)
