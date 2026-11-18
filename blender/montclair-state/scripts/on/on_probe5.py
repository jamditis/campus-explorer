import bpy
from mathutils import Vector
for nm in ['Schmitt Hall walls','Finley Hall walls']:
    w=bpy.data.objects.get(nm)
    if not w: print('MISSING',nm); continue
    me=w.data; M=w.matrix_world
    for f in me.polygons:
        vs=[M@me.vertices[i].co for i in f.vertices]; cc=sum(vs,Vector())/len(vs)
        if abs(f.normal.z)<0.1 and -26<cc.x<-15 and 110<cc.y<126 and f.area>1:
            xy=sorted(set((round(v.x,2),round(v.y,2)) for v in vs))
            print(nm[:7],f.index,tuple(round(n,2) for n in f.normal),xy[0],xy[-1],round(min(v.z for v in vs),2),round(max(v.z for v in vs),2))
r=bpy.data.objects['Schmitt Hall roof (LiDAR)']; me=r.data; M=r.matrix_world
zs=[(M@v.co) for v in me.vertices]; zs=[p for p in zs if -24<p.x<-17 and 112<p.y<124]
print('ROOF n',len(zs),'zmin',round(min(p.z for p in zs),2) if zs else None,'zmax',round(max(p.z for p in zs),2) if zs else None)
