import bpy,resource
print('P rss',resource.getrusage(resource.RUSAGE_SELF).ru_maxrss//1024)
for o in bpy.context.scene.objects: print('P obj',o.name,o.type,len(o.data.vertices) if o.type=='MESH' else '',[m.type+':'+m.name for m in o.modifiers][:6])
