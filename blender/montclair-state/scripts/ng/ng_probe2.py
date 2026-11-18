import bpy, mathutils
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
V=mathutils.Vector
def rc(o,d,lab):
    hit,loc,n,i,ob,m=sc.ray_cast(dg,V(o),V(d).normalized())
    print("RC",lab,o,d,ob.name if ob else None, [round(c,2) for c in loc] if hit else None)
P=(8.3,8.0,143.55)
for d in [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1),(1,1,-0.8)]: rc(P,d,'bal')
for xy in [(-17,-8),(0,10),(-10,10),(5,10),(12,10),(12,-5),(18,-15),(7,18)]:
    o=(xy[0],xy[1],170); hit,loc,n,i,ob,m=sc.ray_cast(dg,V(o),V((0,0,-1)))
    seq=[]
    for k in range(6):
        if not hit: break
        seq.append((ob.name[:50],round(loc.z,2)))
        o=loc+V((0,0,-0.01)); hit,loc,n,i,ob,m=sc.ray_cast(dg,o,V((0,0,-1)))
    print("DOWN",xy,seq)
for xy in [(-12,9),(-6,12),(2,10),(12,0)]:
    hit,loc,n,i,ob,m=sc.ray_cast(dg,V((xy[0],xy[1],137.9)),V((0,0,-1)))
    print("FLOOR",xy,ob.name if ob else None,round(loc.z,3) if hit else None)
