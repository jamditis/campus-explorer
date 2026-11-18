import bpy, bmesh
w=bpy.data.objects['Calcia Hall walls']; mw=w.matrix_world
me=bpy.data.meshes['PS_backup_Calcia_walls']; bm=bmesh.new(); bm.from_mesh(me)
tops=[]
for e in bm.edges:
    if not e.is_boundary: continue
    a=mw@e.verts[0].co; b=mw@e.verts[1].co
    if min(a.z,b.z)>139 and abs(a.z-b.z)<0.3: tops.append((round((a.z+b.z)/2,2),round((a-b).length,2),tuple(round(x,1) for x in a),tuple(round(x,1) for x in b)))
tops.sort(); print('NTOP',len(tops))
for t in tops: 
    if t[0]<147.3: print('TOP',t)
import collections; print('TOPZ',collections.Counter(round(t[0],1) for t in tops))
