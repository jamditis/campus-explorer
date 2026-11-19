import bpy
o=[o for o in bpy.data.objects if o.name.startswith('WS215_RHD_SE_core_street_level_sidewalk')][0]; M=o.matrix_world
vs=[(i,M@v.co) for i,v in enumerate(o.data.vertices)]
for i,w in sorted(vs,key=lambda t:t[1].x):
    if -257.0<=w.x<=-255.3 and -53.4<=w.y<=-52.6: print('P222 v%d (%.3f,%.3f,%.3f)'%(i,w.x,w.y,w.z))
e=[o for o in bpy.data.objects if o.name.startswith('WS214_N_berm_tip_gap_asphalt')][0]; M=e.matrix_world
print('P222 E nverts',len(e.data.vertices),'npoly',len(e.data.polygons))
for i,v in enumerate(e.data.vertices):
    w=M@v.co
    if -257.0<=w.x<=-255.3 and -53.4<=w.y<=-52.6: print('P222 E v%d (%.3f,%.3f,%.3f)'%(i,w.x,w.y,w.z))
