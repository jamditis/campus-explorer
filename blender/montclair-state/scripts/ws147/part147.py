import bpy, json, resource, os, sys
from mathutils import Vector
P='/workspace/nj-scenes/montclair-state/montclair_state.blend'
R=[json.loads(l) for l in open('/workspace/nj-scenes/montclair-state/scripts/ws147/bboxes.jsonl')]
def ov(b,x0,x1,y0,y1): return b[0]<x1 and b[1]>x0 and b[2]<y1 and b[3]>y0
want=set(['Terrain_LiDAR_DTM_1m','Context_skirt_3DEP_ortho_4km','WS60_terrain_edge_apron_LiDAR_to_skirt','Roads_OSM','Footpaths_OSM','OZ_walk_joints_auto_GN_UNVERIFIED','PA_walk_panel_tone_chips_UNVERIFIED','Sun','Freeman Hall walls','Freeman Hall roof (LiDAR)'])
for r in R:
    if 'bb' not in r or r['t'] not in ('MESH','LIGHT'): continue
    b=r['bb']
    if ov(b,-95,-55,-215,-150) and (b[1]-b[0])<80 and (b[3]-b[2])<80 and not r['hr']: want.add(r['n'])
print("WANT",len(want))
with bpy.data.libraries.load(P, link=False) as (src,dst):
    dst.objects=[n for n in src.objects if n in want]
    dst.worlds=list(src.worlds)[:1]
sc=bpy.context.scene
for o in dst.objects:
    if o: sc.collection.objects.link(o)
if dst.worlds and dst.worlds[0]: sc.world=dst.worlds[0]
for o in list(sc.objects):
    if o.type=='MESH' and o.name in ('Cube',): bpy.data.objects.remove(o)
print("RSS",resource.getrusage(resource.RUSAGE_SELF).ru_maxrss//1024)
bpy.ops.wm.save_as_mainfile(filepath='/workspace/nj-scenes/montclair-state/scripts/ws147/part147.blend')
print("SAVED")
