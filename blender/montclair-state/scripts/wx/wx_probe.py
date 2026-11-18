import bpy, json
from mathutils import Vector
from collections import Counter
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
print('STONE', [o.name for o in bpy.data.objects if 'stone' in o.name.lower() and o.type=='MESH'][:40])
res={}; cnt=Counter()
for xi in range(1240,1500,5):
  for yi in range(2500,3250,10):
    x=xi/10;y=yi/10
    h,loc,n,i,ob,m=sc.ray_cast(dg,Vector((x,y,300)),Vector((0,0,-1)))
    if h:
      res[f'{x},{y}']=(ob.name,round(loc.z,3),round(n.z,2)); cnt[ob.name]+=1
print('TOPS',cnt.most_common(30))
json.dump(res,open('/workspace/nj-scenes/montclair-state/data/wx/probe.json','w'))
