import bpy
from mathutils import Vector
for o in bpy.data.objects:
    if o.type!='MESH': continue
    if not o.name.startswith(('WS117','WS119','WS120','WS107_Chapin','Chapin','WS122','BLD','OSM_b')) and 'Chapin' not in o.name: continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    print('B',o.name[:70],[round(min(v.x for v in bb),2),round(max(v.x for v in bb),2),round(min(v.y for v in bb),2),round(max(v.y for v in bb),2),round(min(v.z for v in bb),2),round(max(v.z for v in bb),2)])
# Footpaths faces in recess box
fp=bpy.data.objects['Footpaths_OSM']; mw=fp.matrix_world; n=0; zs=[]
for p in fp.data.polygons:
    c=mw@p.center
    if -212<c.x<-207 and -204<c.y<-200.3: n+=1; zs.append(round(c.z,2))
print('FP',n,sorted(set(zs)))
# building wall faces near (vertical) in box
dg=bpy.context.evaluated_depsgraph_get()
for o in bpy.data.objects:
    if o.type!='MESH' or 'hapin' not in o.name: continue
    mw=o.matrix_world
    for p in o.data.polygons:
        c=mw@p.center; nn=(mw.to_3x3()@p.normal).normalized()
        if -216<c.x<-207 and -204<c.y<-199 and abs(nn.z)<0.2 and c.z<128 : print('W',o.name[:40],round(c.x,2),round(c.y,2),round(c.z,2),[round(a,2) for a in nn])
