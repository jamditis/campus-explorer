import bpy, json, resource, sys, os
from mathutils import Vector
P='/workspace/nj-scenes/montclair-state/montclair_state.blend'
FIX=os.environ.get('FIX','0')=='1'; TAG=os.environ.get('TAG','before')
def rss(t): print(t,"RSS",resource.getrusage(resource.RUSAGE_SELF).ru_maxrss//1024, flush=True)
R=[json.loads(l) for l in open('/workspace/nj-scenes/montclair-state/scripts/ws147/bboxes.jsonl')]
def ov(b,x0,x1,y0,y1): return b[0]<x1 and b[1]>x0 and b[2]<y1 and b[3]>y0
want=['Terrain_LiDAR_DTM_1m','Freeman Hall walls','Freeman Hall roof (LiDAR)','Footpaths_OSM','Roads_OSM','PA_walk_panel_tone_chips_UNVERIFIED','OZ_walk_joints_auto_GN_UNVERIFIED','WS48_band_street_trees_OSM_lowLOD','Context_skirt_3DEP_ortho_4km','WS60_terrain_edge_apron_LiDAR_to_skirt']
KEEPGN=set(os.environ.get('KEEPGN','').split(','))
for r in R:
    if 'bb' in r and r['t']=='MESH' and r['n'].startswith(('WS14','WS13')) and ov(r['bb'],-95,-55,-215,-150) and not r['hr']: want.append(r['n'])
with bpy.data.libraries.load(P, link=False) as (src,dst):
    dst.objects=list(want); dst.worlds=list(src.worlds)[:1]
sc=bpy.context.scene
for n in ('Cube','Light'):
    if n in bpy.data.objects: bpy.data.objects.remove(bpy.data.objects[n])
for o in list(bpy.data.objects):
    if o.type=='MESH' and o.name not in want: o.hide_render=True   # GN helper objects dragged in
keep=[bpy.data.objects.get(n) for n in want]
for o in keep:
    if o:
        if o.name not in KEEPGN:
            for m in list(o.modifiers): o.modifiers.remove(m)
        if o.name not in sc.collection.objects: sc.collection.objects.link(o)
if dst.worlds and dst.worlds[0]: sc.world=dst.worlds[0]
sun=bpy.data.objects.new('S',bpy.data.lights.new('S','SUN')); sun.data.energy=3; sun.rotation_euler=(0.8,0.2,2.4); sc.collection.objects.link(sun)
rss("APPENDED %d"%len(want))
if FIX: exec(open('/workspace/nj-scenes/montclair-state/scripts/ws147/fix147_53.py').read())
t=bpy.data.objects['Terrain_LiDAR_DTM_1m']
def gz(x,y):
    h=None
    for p in t.data.polygons:
        pass
    return None
cam=bpy.data.objects['Camera']
# camera = WS143_CAM_eye_forecourt_from_N_aisle approx (ground ~129 there)
loc=Vector((-64.5,-160,129.9+1.7)); tgt=Vector((-73,-176,128.6+0.5))
cam.location=loc; cam.data.lens=26; cam.data.clip_start=0.1
cam.rotation_euler=(tgt-loc).to_track_quat('-Z','Y').to_euler(); sc.camera=cam
sc.render.engine='CYCLES'; sc.cycles.device='CPU'; sc.cycles.samples=12; sc.render.resolution_x=640; sc.render.resolution_y=360; sc.render.resolution_percentage=100
sc.render.image_settings.file_format='JPEG'
sc.render.filepath='/workspace/nj-scenes/montclair-state/scripts/ws147/prev147_%s.jpg'%TAG
bpy.ops.render.render(write_still=True); rss("RENDERED")
