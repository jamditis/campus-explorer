import bpy
for o in bpy.data.objects:
    if o.name.startswith('WS70_gap_strip_grass'):
        M=o.matrix_world; print('P223 obj',o.name,'mods',[(m.name,m.type) for m in o.modifiers],'nv',len(o.data.vertices))
        for i,v in enumerate(o.data.vertices):
            w=M@v.co
            if -249.8<=w.x<=-248.85 and -55.2<=w.y<=-54.35: print('P223 v%d (%.3f,%.3f,%.3f)'%(i,w.x,w.y,w.z))
