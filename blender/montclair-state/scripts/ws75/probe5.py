import bpy,collections
o=bpy.data.objects['Roads_OSM']; mw=o.matrix_world
c=collections.Counter()
for p in o.data.polygons:
    q=mw@p.center
    if -320<q.x<-200 and -170<q.y<-60: c[(int(q.x//5*5),int(q.y//5*5))]+=1
print('R5',sorted(c.items()))
