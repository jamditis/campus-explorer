import bpy,collections
r=bpy.data.objects['Feliciano School of Business roof (LiDAR)']; mw=r.matrix_world; R=mw.to_3x3()
print('SLOTS',[s.material.name if s.material else None for s in r.material_slots])
h=collections.Counter(); A=collections.Counter()
for p in r.data.polygons:
    n=(R@p.normal).normalized(); b='flat' if abs(n.z)>0.95 else ('slope' if abs(n.z)>0.3 else 'vert')
    h[(p.material_index,b)]+=1; A[(p.material_index,b)]+=p.area
for k in sorted(h): print('H',k,h[k],round(A[k],1))
# wall-material faces above pavilion
for p in r.data.polygons:
    c=mw@p.center
    if r.material_slots[p.material_index].material.name=='Wall_stucco_mission' and -224<c.x<-204 and 164<c.y<192 and c.z>158:
        n=(R@p.normal).normalized(); print('W',p.index,round(c.x,1),round(c.y,1),round(c.z,1),round(n.x,2),round(n.y,2),round(n.z,2),round(p.area,1))
print('Z',round(min((mw@v.co).z for v in r.data.vertices),1),round(max((mw@v.co).z for v in r.data.vertices),1))
