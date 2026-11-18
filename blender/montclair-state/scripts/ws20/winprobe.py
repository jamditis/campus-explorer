import bpy
from mathutils import Vector
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
# direction from the Life N camera toward the wall
cam=Vector((33.9,121.8,138.6))
for tx in (19,20.5,22,23.5,25,30.5,32):
  for tz in (139.5,143.5):
    # wall near y = 105.2 - 0.27*(x-15) roughly
    ty=105.4-0.29*(tx-15)
    d=(Vector((tx,ty,tz))-cam).normalized(); o=cam.copy(); hits=[]
    for k in range(4):
        h,loc,n,i,ob,_=sc.ray_cast(dg,o,d,distance=60)
        if not h: break
        hits.append((ob.name[:34],round((loc-cam).length,2)))
        o=loc+d*0.002
    print('H',tx,tz,hits)
