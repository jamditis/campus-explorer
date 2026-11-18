import bpy, json, resource, sys
from mathutils import Vector
P='/workspace/nj-scenes/montclair-state/montclair_state.blend'
def rss(t): print(t,"RSS",resource.getrusage(resource.RUSAGE_SELF).ru_maxrss//1024, flush=True)
R=[json.loads(l) for l in open('/workspace/nj-scenes/montclair-state/scripts/ws147/bboxes.jsonl')]
def ov(b,x0,x1,y0,y1): return b[0]<x1 and b[1]>x0 and b[2]<y1 and b[3]>y0
want=['Terrain_LiDAR_DTM_1m','Context_skirt_3DEP_ortho_4km','WS60_terrain_edge_apron_LiDAR_to_skirt','Roads_OSM','Footpaths_OSM','OZ_walk_joints_auto_GN_UNVERIFIED','PA_walk_panel_tone_chips_UNVERIFIED','Freeman Hall walls']
for r in R:
    if 'bb' in r and r['t']=='MESH' and r['n'].startswith(('WS14','WS13')) and ov(r['bb'],-95,-55,-215,-150) and not r['hr']: want.append(r['n'])
with bpy.data.libraries.load(P, link=False) as (src,dst):
    dst.objects=want
sc=bpy.context.scene
for o in dst.objects:
    if o and o.name not in sc.collection.objects: sc.collection.objects.link(o)
for n in ('Cube',):
    if n in bpy.data.objects: bpy.data.objects.remove(bpy.data.objects[n])
rss("APPENDED %d"%len(want))
bpy.ops.wm.save_as_mainfile(filepath='/workspace/nj-scenes/montclair-state/scripts/ws147/part147.blend')
rss("SAVED")
