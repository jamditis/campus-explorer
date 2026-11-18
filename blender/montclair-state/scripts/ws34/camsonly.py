from mathutils import Vector
sc=bpy.context.scene
base=bpy.data.objects.get('Sun')
CAMS={'WS34_CAM_oblique_Cole_plaza_west_edge_from_SW':((-238,-138,150),(-200,-88,127.5),28),
 'WS34_CAM_eye_Cole_plaza_SW_corner_from_S':((-195.5,-106,None),(-206,-84,127.6),24),
 'WS34_CAM_eye_Cole_plaza_west_from_CollegeAve':((-224,-92,None),(-199,-88,128.2),26),
 'WS34_CAM_closeup_Cole_plaza_west_edge_steps':((-205,-98,None),(-200.5,-90,127.6),30)}
dg=bpy.context.evaluated_depsgraph_get()
ter=bpy.data.objects['Terrain_LiDAR_DTM_1m']
for n,(loc,tgt,lens) in CAMS.items():
    if loc[2] is None:
        # terrain-only ray so the camera never lands in a tree crown
        e=ter.evaluated_get(dg); mi=ter.matrix_world.inverted()
        ok,hp,_,_=e.ray_cast(mi@Vector((loc[0],loc[1],200)),(mi.to_3x3()@Vector((0,0,-1))).normalized())
        z=(ter.matrix_world@hp).z if ok else 136
        loc=(loc[0],loc[1],z+(1.6 if 'eye' in n else 1.3)); print('cam',n,round(loc[2],2))
    c=bpy.data.objects.get(n)
    if not c:
        cd=bpy.data.cameras.new(n); c=bpy.data.objects.new(n,cd); sc.collection.objects.link(c)
    c.location=loc; c.data.lens=lens; c.data.clip_start=0.1; c.data.clip_end=3000
    c.rotation_euler=(Vector(tgt)-Vector(loc)).to_track_quat('-Z','Y').to_euler()
