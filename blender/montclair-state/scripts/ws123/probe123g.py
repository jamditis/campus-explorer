import bpy
dg=bpy.context.evaluated_depsgraph_get()
for nm in ('Terrain_LiDAR_DTM_1m','WS113_terrain_fan_fill','WS117_Chapin_W_entrance_landing','WS117_Chapin_W_entrance_cheek','WS119_Chapin_W_terrace_wall_coping','WS60_terrain_edge','Context_skirt','BD_farfield','WS119_Chapin_W'):
    for o in [o for o in bpy.data.objects if o.name.startswith(nm) and o.type=='MESH']:
        e=o.evaluated_get(dg); m=e.to_mesh(); mw=o.matrix_world; hits=[]
        for p in m.polygons:
            c=mw@p.center
            if -211.0<c.x<-209.0 and -197.8<c.y<-195.0: hits.append((round(c.x,2),round(c.y,2),round(c.z,3),round(p.normal.z,2)))
        e.to_mesh_clear()
        if hits: print('G',o.name[:60],len(hits),sorted(hits,key=lambda h:-h[2])[:6])
