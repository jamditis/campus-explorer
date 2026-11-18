import bpy, resource
P='/workspace/nj-scenes/montclair-state/montclair_state.blend'
want=[l for l in open('/workspace/nj-scenes/montclair-state/scripts/ws151/objnames.txt').read().split('\n') if l.startswith(('WS150_Lot9','WS148_Lot9','WS142_Lot9','WS135a_Skyline_Way','WS145_walk','WS147_walk','WS143_Freeman','Curbs_granite_OSM'))]+['Terrain_LiDAR_DTM_1m']
with bpy.data.libraries.load(P, link=False) as (src,dst): dst.objects=list(want)
for o in dst.objects:
    if o.name.startswith('Terrain'):
        for m in list(o.modifiers): o.modifiers.remove(m)
    bpy.context.scene.collection.objects.link(o)
bpy.context.view_layer.update()
print("RSS load",resource.getrusage(resource.RUSAGE_SELF).ru_maxrss//1024)
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws151/fix151.py').read())
bpy.ops.wm.save_as_mainfile(filepath='/tmp/test151.blend')
print("RSS end",resource.getrusage(resource.RUSAGE_SELF).ru_maxrss//1024)
