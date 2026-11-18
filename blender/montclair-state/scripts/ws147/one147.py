import bpy, resource, sys
n=sys.argv[-1]
with bpy.data.libraries.load('/workspace/nj-scenes/montclair-state/montclair_state.blend', link=False) as (src,dst):
    dst.objects=[n]
print("APP",n,"RSS",resource.getrusage(resource.RUSAGE_SELF).ru_maxrss//1024, len(bpy.data.objects), len(bpy.data.images), len(bpy.data.meshes))
o=dst.objects[0]
for m in o.modifiers:
    if m.type=='NODES':
        print(" MOD",m.name,[ (k, getattr(v,'name',v)) for k,v in m.items() if hasattr(v,'name')])
print("OBJS",[x.name[:40] for x in bpy.data.objects][:30])
