import bpy
from collections import Counter
dg=bpy.context.evaluated_depsgraph_get()
for n in ('Footpaths_OSM','Roads_OSM'):
    o=bpy.data.objects[n]; e=o.evaluated_get(dg); me=e.to_mesh(); W=o.matrix_world; sp=[]
    for p in me.polygons:
        c=W@p.center
        if 195<c.x<250 and 135<c.y<258 and abs(p.normal.z)<0.3:
            zs=[(W@me.vertices[v].co).z for v in p.vertices]; sp.append((round(max(zs)-min(zs),2),round(c.x,1),round(c.y,1)))
    sp.sort(reverse=True); print(n,'vert faces',len(sp),'span>0.3',sum(1 for s in sp if s[0]>0.3),sp[:8])
    e.to_mesh_clear()
