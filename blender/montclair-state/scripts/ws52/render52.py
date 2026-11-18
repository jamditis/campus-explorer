import bpy, os, bmesh
from datetime import datetime
from mathutils import Vector
from mathutils.bvhtree import BVHTree
sc=bpy.context.scene; R='/workspace/nj-scenes/montclair-state'
dg=bpy.context.evaluated_depsgraph_get()
def bvh(n):
    o=bpy.data.objects[n]; e=o.evaluated_get(dg); m=e.to_mesh(); bm=bmesh.new(); bm.from_mesh(m); bm.transform(o.matrix_world); t=BVHTree.FromBMesh(bm); bm.free(); e.to_mesh_clear(); return t
TT=[bvh(n) for n in ('Terrain_LiDAR_DTM_1m','Context_skirt_3DEP_ortho_4km')]
def gz(x,y): return max([t.ray_cast(Vector((x,y,200)),Vector((0,0,-1)))[0].z for t in TT if t.ray_cast(Vector((x,y,200)),Vector((0,0,-1)))[0] is not None]+[0])
def cam(n,loc,tgt,lens,eye=None):
    if eye is not None: loc=(loc[0],loc[1],gz(loc[0],loc[1])+eye)
    c=bpy.data.objects.get(n)
    if not c: c=bpy.data.objects.new(n,bpy.data.cameras.new(n)); sc.collection.objects.link(c)
    c.location=loc; c.data.lens=lens; c.data.clip_start=0.1; c.data.clip_end=3000
    c.rotation_euler=(Vector(tgt)-Vector(loc)).to_track_quat('-Z','Y').to_euler()
def camz(n,loc,tgt,lens,eye=None,th=1.0):
    tgt=(tgt[0],tgt[1],gz(tgt[0],tgt[1])+th); cam(n,loc,tgt,lens,eye)
camz('WS49_CAM_oblique_band_trees_SE_from_campus',(0,-20,235),(330,-430),30,None,0.0)
camz('WS49_CAM_eye_band_from_Kasser_frontage',(-205,-125,0),(-480,-330),35,1.6,6.0)
camz('WS49_CAM_eye_band_from_CCOM_east',(35,-60,0),(380,-320),35,1.6,6.0)
camz('WS49_CAM_closeup_band_crowns',(210.7,-271.8,0),(245.7,-246.8),35,8.0,4.0)
base=bpy.data.objects.get('Sun'); sc.world=bpy.data.worlds['WP2_World_GOLDEN']
if base: base.hide_render=True
for k in ('MORNING','GOLDEN','OVERCAST'):
    o=bpy.data.objects.get('WP2_Sun_'+k)
    if o: o.hide_render=(k!='GOLDEN')
cx0,cx1,cy0,cy1=map(float,os.environ.get('CULL','-9999,9999,-9999,9999').split(','))
for o in sc.objects:
    if o.type in ('CAMERA','LIGHT') or o.hide_render or o.name.startswith('Terrain_LiDAR'): continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]; xs=[v.x for v in bb]; ys=[v.y for v in bb]
    if max(xs)<cx0 or min(xs)>cx1 or max(ys)<cy0 or min(ys)>cy1: o.hide_render=True
ts=datetime.now().strftime('%Y%m%d-%H%M')
for ONLY,LABEL in [x.split('=') for x in os.environ['CAMS'].split(',') if x]:
    sc.camera=bpy.data.objects[ONLY]
    sc.render.engine='CYCLES'; sc.cycles.device='CPU'; sc.cycles.samples=int(os.environ.get('SAMP','24')); sc.cycles.use_denoising=True
    sc.render.resolution_x=1280; sc.render.resolution_y=720; sc.render.resolution_percentage=int(os.environ.get('PCT','75'))
    sc.render.image_settings.file_format='JPEG'; sc.render.image_settings.quality=90
    sc.render.threads_mode='FIXED'; sc.render.threads=4; sc.render.use_simplify=True; sc.render.simplify_subdivision_render=min(sc.render.simplify_subdivision_render,2); sc.cycles.texture_limit_render=os.environ.get('TEXLIM','2048')
    fp=f"{R}/renders/{os.environ.get('DIR','wip')}/{ts}_{LABEL}_{os.environ.get('OUT_TAG','GOLDEN_ws35_goldenhour')}.jpg"; sc.render.filepath=fp
    bpy.ops.render.render(write_still=True); print('WROTE',fp,flush=True)
