import bpy
from mathutils import Vector
X0,X1,Y0,Y1=-130.4,-114.9,-265.4,-234.2
for nm in ('WS60_terrain_edge_apron_LiDAR_to_skirt','Terrain_LiDAR_DTM_1m'):
    o=bpy.data.objects[nm]; mw=o.matrix_world; me=o.data
    print('OBJ',nm,len(me.vertices),len(me.polygons),[m.name for m in o.modifiers])
    for p in me.polygons:
        V=[mw@me.vertices[i].co for i in p.vertices]
        if max(v.x for v in V)>=X0 and min(v.x for v in V)<=X1 and max(v.y for v in V)>=Y0 and min(v.y for v in V)<=Y1:
            print(' F',p.index,[ '(%.1f,%.1f,%.2f)'%(v.x,v.y,v.z) for v in V])
