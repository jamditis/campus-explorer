import bpy
for n in ('Calcia Hall walls','Calcia Hall roof (LiDAR)','Calcia_coping_parapet','PS_backup_Calcia_walls'):
    if n in bpy.data.objects: o=bpy.data.objects[n]; P=[o.matrix_world@v.co for v in o.data.vertices]
    else: o=bpy.data.objects['Calcia Hall walls']; P=[o.matrix_world@v.co for v in bpy.data.meshes[n].vertices]
    zs=sorted(set(round(p.z,2) for p in P)); print('Z',n,len(P),zs[:6],zs[-6:])
o=bpy.data.objects['Calcia Hall roof (LiDAR)']; P=[o.matrix_world@v.co for v in o.data.vertices]
print('ROOF minmax x',min(p.x for p in P),max(p.x for p in P),'y',min(p.y for p in P),max(p.y for p in P))
w=bpy.data.objects['Calcia Hall walls']; P=[w.matrix_world@v.co for v in w.data.vertices]
print('WALL minmax x',min(p.x for p in P),max(p.x for p in P),'y',min(p.y for p in P),max(p.y for p in P))
import collections
c=collections.Counter(round(p.z,1) for p in P if p.z>144); print('WALL top z hist',sorted(c.items())[-8:])
c=collections.Counter(round((o.matrix_world@v.co).z,1) for v in o.data.vertices); print('ROOF z hist',sorted(c.items())[:10])
