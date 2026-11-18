import bpy,bmesh
from mathutils import Vector
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
o=bpy.data.objects['Roads_OSM']
print('SLOTS',[(i,s.material.name if s.material else None) for i,s in enumerate(o.material_slots)],len(o.data.polygons),[m.name+':'+m.type for m in o.modifiers],o.hide_render)
mw=o.matrix_world; cnt={}; cov={}
sel=[]
for p in o.data.polygons:
    c=mw@p.center
    if -345<c.x<-222 and -165<c.y<-85:
        k=p.material_index; cnt[k]=cnt.get(k,0)+1
        hit,loc,nor,idx,ob,mx=sc.ray_cast(dg,c+Vector((0,0,30)),Vector((0,0,-1)))
        top=ob.name[:30] if hit else None
        cov[(k,top)]=cov.get((k,top),0)+1
        sel.append((p.index,k,top,round(c.x),round(c.y)))
print('CNT',cnt); print('COV',sorted(cov.items(),key=lambda a:-a[1])[:20])
import json; json.dump(sel,open('/workspace/nj-scenes/montclair-state/scripts/ws75/roads_sel.json','w'))
xs=[s for s in sel if s[2] and s[2].startswith('Roads_OSM')]
import collections
print('VISIBLE cells by 10m',collections.Counter((s[3]//10*10,s[4]//10*10) for s in xs).most_common(30))
