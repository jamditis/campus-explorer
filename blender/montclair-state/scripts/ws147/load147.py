import bpy, resource
print("LOADED_RSS_MB",resource.getrusage(resource.RUSAGE_SELF).ru_maxrss//1024, len(bpy.data.objects), len(bpy.data.images))
