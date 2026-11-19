import bpy
g=bpy.data.objects['WS70_gap_strip_grass_berms']; M=g.matrix_world
for v in g.data.vertices:
    w=M@v.co
    if -249.0<=w.x<=-247.0 and -55.5<=w.y<=-52.5: print('P221 G %d %.3f %.3f %.3f'%(v.index,*w))
