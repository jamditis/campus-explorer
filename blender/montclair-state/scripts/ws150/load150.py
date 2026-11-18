import bpy, resource
def rss():
    for l in open('/proc/self/status'):
        if l.startswith('VmRSS'): return int(l.split()[1])//1024
print("LOAD150 now",rss(),"peak",resource.getrusage(resource.RUSAGE_SELF).ru_maxrss//1024, "objs",len(bpy.data.objects),"meshes",len(bpy.data.meshes))
