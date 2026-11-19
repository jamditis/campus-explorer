import bpy
o=bpy.data.objects['WS72_Kasser_SW_RHD_core_sidewalk_landing_UNVERIFIED_width']; M=o.matrix_world
for i,v in enumerate(o.data.vertices):
    w=M@v.co
    if -249.3<=w.x<=-247.0 and -54.0<=w.y<=-52.5: print('P222 v%d (%.3f,%.3f,%.3f)'%(i,w.x,w.y,w.z))
for p in o.data.polygons:
    c=M@p.center
    if -249.3<=c.x<=-247.0 and -54.0<=c.y<=-52.5: print('P222 f%d %s nz %.2f'%(p.index,list(p.vertices),p.normal.z))
