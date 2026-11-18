import bpy
from mathutils import Vector
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
for o in bpy.data.objects:
    if 'planting_beds' in o.name or o.name.startswith(('WS3_Cole_plaza_paving','Footpaths_OSM','WS5_','WS8_')):
        if o.type=='MESH':
            bb=[o.matrix_world@Vector(c) for c in o.bound_box]
            print('OBJ',o.name,len(o.data.polygons),'x',round(min(v.x for v in bb),1),round(max(v.x for v in bb),1),'y',round(min(v.y for v in bb),1),round(max(v.y for v in bb),1),'z',round(min(v.z for v in bb),2),round(max(v.z for v in bb),2), 'hide',o.hide_render)
bed=[o for o in bpy.data.objects if 'COLE_planting_beds' in o.name]
for name in ('WS3_Cole_plaza_paving','Footpaths_OSM'):
    o=bpy.data.objects.get(name)
    if not o: continue
    ev=o.evaluated_get(dg); me=ev.to_mesh(); mw=o.matrix_world
    cov=[];
    for p in me.polygons:
        c=mw@p.center
        if not(-140<c.x<-55 and -110<c.y<-30): continue
        if p.normal.z<0.7: continue
        oo=c+Vector((0,0,3))
        for i in range(8):
            r=sc.ray_cast(dg,oo,Vector((0,0,-1)))
            if not r[0]: break
            nm=r[4].name
            if 'planting_beds' in nm or 'mulch' in nm.lower():
                if r[1].z>c.z-0.01: cov.append((p.index,round(c.x,1),round(c.y,1),round(r[1].z-c.z,3),nm)); 
                break
            if nm==name or nm.startswith('Terrain'): break
            oo=r[1]+Vector((0,0,-0.002))
    print('COVERED',name,len(cov))
    for x in cov[:80]: print(' ',x)
