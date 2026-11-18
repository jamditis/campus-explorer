import bpy
r=bpy.data.objects['Feliciano School of Business roof (LiDAR)']; mw=r.matrix_world
B=(-224,-206,164,180)
L=[]
for p in r.data.polygons:
    c=mw@p.center
    if B[0]<c.x<B[1] and B[2]<c.y<B[3]:
        n=(mw.to_3x3()@p.normal).normalized(); L.append((round(c.z,1),round(c.x,1),round(c.y,1),round(n.z,2),round(n.y,2),round(p.area,1),p.material_index))
L.sort()
print('N',len(L))
import collections; h=collections.Counter(int(t[0]) for t in L); print('HIST',sorted(h.items()))
for t in L: 
    if t[0]<162: print('F',t)
w=bpy.data.objects['Feliciano School of Business walls']
for p in w.data.polygons:
    c=w.matrix_world@p.center
    if c.y<185 : print('W',p.index,round(c.x,1),round(c.y,1),round(c.z,1),[round(x,2) for x in p.normal],round(p.area,1), [round((w.matrix_world@w.data.vertices[v].co).z,1) for v in p.vertices])
