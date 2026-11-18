import bpy,json
from mathutils import Vector
out={}
names=['WS3_Cole_plaza_paving_20261109','Footpaths_OSM','COLE_planting_beds_smooth_bu','TZ_Cole_north_addition_UNVERIFIED','Susan A. Cole Hall walls']
for n in names:
  o=bpy.data.objects[n]; mw=o.matrix_world; fl=[]
  for f in o.data.polygons:
    c=mw@f.center
    if -140<c.x<-60 and -95<c.y<-20:
      fl.append({'i':f.index,'m':f.material_index,'z':round(c.z,2),'v':[[round((mw@o.data.vertices[i].co)[k],2) for k in range(2)] for i in f.vertices]})
  out[n]=fl
for o in bpy.data.objects:
  if o.name.startswith(('Lamp_','Bench_','WS4_')) or 'sign' in o.name.lower():
    p=o.matrix_world.translation
    if -140<p.x<-60 and -95<p.y<-20: out.setdefault('_pts',[]).append([o.name,round(p.x,2),round(p.y,2),round(p.z,2),round(o.rotation_euler.z,3),o.parent.name if o.parent else None])
json.dump(out,open('/workspace/nj-scenes/montclair-state/scripts/ws5/dump.json','w'))
print('DUMPED',{k:len(v) for k,v in out.items()})
