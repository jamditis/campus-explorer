import bpy,json
rows=[]
for me in bpy.data.meshes:
    rows.append((len(me.polygons),len(me.vertices),me.name,me.users))
rows.sort(reverse=True)
tot=sum(r[0] for r in rows)
dm=[r for r in rows if r[2].startswith('dM')]
print('SRCAUDIT total_faces',tot,'meshes',len(rows))
print('SRCAUDIT dM_faces',sum(r[0] for r in dm),'dM_meshes',len(dm))
for r in rows[:15]: print('SRCAUDIT top',r)
