import bpy, math
from mathutils import Vector
O=bpy.data.objects
for nm in ['CCOM newsroom seated people placeholders (my, GN instances)','CCOM newsroom task chairs (mx, GN instances)','CCOM newsroom grid spots (mx, GN instances)','CCOM newsroom studio lighting grid (mw)']:
    o=O[nm]; print(nm, [round(x,3) for x in o.matrix_world.translation], o.matrix_world.to_euler(), len(o.data.vertices))
pp=O['CCOM newsroom seated people placeholders (my, GN instances)']
for i,v in enumerate(pp.data.vertices):
    print('person',i,[round(x,3) for x in v.co], round(pp.data.attributes['rot'].data[i].vector[2],3))
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
L=math.hypot(0.238,0.9713); d=Vector((0.238/L,0.9713/L,0)); n=Vector((-0.9713/L,0.238/L,0)); C0=20.36; T0=0.012
def P(u,t,z): return d*u+n*(C0+T0+t)+Vector((0,0,z))
for u,t in ((-14.19,-2.425),(-14.19,-4.925),(-14.19,-7.425),(-6.69,-2.425),(-6.69,-7.425)):
    r=sc.ray_cast(dg,P(u,t,145.6),Vector((0,0,1)))
    print('up',u,t,r[0], round(r[1].z,3) if r[0] else None, r[4].name if r[0] else None)
