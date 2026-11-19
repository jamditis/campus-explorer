import bpy
g=bpy.data.objects['WS70_gap_strip_grass_berms']; M=g.matrix_world
print('P221 WS70 nv',len(g.data.vertices),'mods',[m.type for m in g.modifiers])
for v in g.data.vertices:
    w=M@v.co
    if -252.5<=w.x<=-248.5 and -56.2<=w.y<=-54.0: print('P221 G %d %.3f %.3f %.3f'%(v.index,*w))
