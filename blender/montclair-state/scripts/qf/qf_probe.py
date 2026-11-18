import bpy, json, math
from mathutils import Vector
CN='Center for Computing and Information Science'
poly=[Vector((x,y)) for x,y in json.load(open('north/data/day_heroes/day7_geom.json'))['buildings'][CN]['poly_m']][:-1]
area=sum(poly[i].x*poly[(i+1)%len(poly)].y-poly[(i+1)%len(poly)].x*poly[i].y for i in range(len(poly)))/2
print('AREA',area)
W=bpy.data.objects[CN+' walls']
segs=[]
for p in W.data.polygons:
    if abs(p.normal.z)>0.2: continue
    vs=[W.matrix_world@W.data.vertices[i].co for i in p.vertices]
    segs.append((Vector((sum(v.x for v in vs)/len(vs),sum(v.y for v in vs)/len(vs))),min(v.z for v in vs),max(v.z for v in vs)))
for i in range(len(poly)):
    a,b=poly[i],poly[(i+1)%len(poly)]; e=b-a; t=e.normalized(); n=Vector((t.y,-t.x)) if area>0 else Vector((-t.y,t.x))
    m=(a+b)/2; ss=[s for s in segs if (s[0]-m).length<e.length/2+0.5 and abs((s[0]-a).cross(t))<1.0]
    print('EDGE',i,tuple(round(c,2) for c in a),tuple(round(c,2) for c in b),'L',round(e.length,2),'n',tuple(round(c,2) for c in n),'az',round(math.degrees(math.atan2(n.y,n.x))),'zb',round(min([s[1] for s in ss]),2) if ss else None,'zt',round(max([s[2] for s in ss]),2) if ss else None)
for o in bpy.data.objects:
    if 'College Hall' in o.name and o.type=='MESH':
        bb=[o.matrix_world@Vector(c) for c in o.bound_box]; print('CH',o.name,round(sum(v.x for v in bb)/8,1),round(sum(v.y for v in bb)/8,1),round(max(v.z for v in bb),1))
for o in bpy.data.collections[CN].all_objects: print('COL',o.name,o.type,o.hide_render, len(o.data.polygons) if o.type=='MESH' else '')
for o in bpy.data.objects:
    if 'CCIS' in o.name or CN in o.name: print('OBJ',o.name,o.hide_render,[m.name for m in o.data.materials] if o.type=='MESH' else '')
print('DOORS',list(bpy.context.scene.get('qe_door_pts',[])))
R=bpy.data.objects[CN+' roof (LiDAR)']; print('ROOFMODS',[m.name for m in R.modifiers],[s.material.name if s.material else None for s in R.material_slots])
