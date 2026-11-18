import bpy, json
from mathutils import Vector
CN='Center for Computing and Information Science'
R=bpy.data.objects[CN+' roof (LiDAR)']; dg=bpy.context.evaluated_depsgraph_get(); Re=R.evaluated_get(dg); Rinv=R.matrix_world.inverted()
def roof_at(xy):
    o=Rinv@Vector((xy.x,xy.y,200)); d=(Rinv.to_3x3()@Vector((0,0,-1))).normalized()
    ok,loc,n,i=Re.ray_cast(o,d); return round((R.matrix_world@loc).z,2) if ok else None
poly=[Vector((x,y)) for x,y in json.load(open('north/data/day_heroes/day7_geom.json'))['buildings'][CN]['poly_m']][:-1]
for i,u in ((0,5),(0,15),(12,5),(12,31),(15,16),(9,7)):
    a,b=poly[i],poly[(i+1)%len(poly)]; t=(b-a).normalized(); n=Vector((t.y,-t.x))
    print('EAVE',i,u,[(o,roof_at(a+t*u+n*o)) for o in (-1.0,-0.3,0.0,0.3,0.6,0.9,1.2,1.6)])
sc=bpy.context.scene
for i,u in ((0,5),(12,5)):
    a,b=poly[i],poly[(i+1)%len(poly)]; t=(b-a).normalized(); n=Vector((t.y,-t.x))
    for o in (0.5,1.0):
        p=a+t*u+n*o; ok,loc,nn,ix,ob,mx=sc.ray_cast(dg,Vector((p.x,p.y,200)),Vector((0,0,-1)))
        print('SCN',i,u,o,ok and round(loc.z,2),ob.name[:50] if ok else None)
