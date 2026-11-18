# pu prep (read-only): Calcia wall faces that straddle corners / short return faces (corner-bay candidates still shader-only)
import bpy, json
from mathutils import Vector
w=bpy.data.objects['Calcia Hall walls']; me=bpy.data.meshes['PS_backup_Calcia_walls']; mw=w.matrix_world; uv=me.uv_layers['facade'].data; out=[]
for p in me.polygons:
    n=mw.to_3x3()@p.normal
    if abs(n.z)>0.1: continue
    U=[uv[l].uv for l in p.loop_indices]; c=mw@p.center
    out.append(dict(i=p.index,c=[round(x,3) for x in c],n=[round(n.x,3),round(n.y,3)],area=round(p.area,2),u=[round(min(q.x for q in U),2),round(max(q.x for q in U),2)],v=[round(min(q.y for q in U),2),round(max(q.y for q in U),2)]))
short=[f for f in out if f['u'][1]-f['u'][0]<2.4]
json.dump(dict(faces=out,short_faces=short,note='pu prep: uncut Calcia wall faces (PS_backup_Calcia_walls); short (<2.4 m) faces = corner-bay/return candidates'),open('data/pu/prep_calcia_cornerbays.json','w'))
print('PREP faces',len(out),'short',len(short))
