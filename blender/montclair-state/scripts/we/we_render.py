import bpy, os
from mathutils import Vector
from datetime import datetime
from mathutils.bvhtree import BVHTree
R='/workspace/nj-scenes/montclair-state'; os.chdir(R)
O=bpy.data.objects; sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
def bvh(o):
    e=o.evaluated_get(dg); m=e.to_mesh(); b=BVHTree.FromPolygons([o.matrix_world@v.co for v in m.vertices],[tuple(p.vertices) for p in m.polygons]); e.to_mesh_clear(); return b
G=[bvh(O[n]) for n in O.keys() if O[n].type=='MESH' and n.startswith(('WV_stone','QW_DTM','Terrain_LiDAR'))]
def gz(x,y):
    z=[h[0].z for b in G for h in [b.ray_cast(Vector((x,y,500)),Vector((0,0,-1)))] if h[0] is not None]; return max(z) if z else 136.3
n='WE_CAM_closeup_stone_footway_junction_from_SE'
px,py,tx,ty=[float(v) for v in os.environ.get('CAMP','148.5,289.0,142.5,295.5').split(',')]
P=Vector((px,py,gz(px,py)+float(os.environ.get('CAMH','1.3')))); T=Vector((tx,ty,gz(tx,ty)+0.05))
cam=O.get(n) or bpy.data.objects.new(n,bpy.data.cameras.new(n))
if n not in sc.collection.all_objects: O['WA2_CAM_closeup_richardson_west_walk_edge'].users_collection[0].objects.link(cam)
cam.location=P; cam.data.lens=float(os.environ.get('LENS','28')); cam.data.clip_start=.1; cam.data.clip_end=5000
cam.rotation_euler=(T-P).to_track_quat('-Z','Y').to_euler()
if os.environ.get('SAVECAM')=='1': bpy.ops.wm.save_mainfile(); print('SAVED',len(O),flush=True)
ts=datetime.now().strftime('%Y%m%d-%H%M'); suf=os.environ.get('SUF','we')
sc.render.engine='CYCLES'; sc.cycles.device='CPU'; sc.cycles.samples=int(os.environ.get('SAMP','24')); sc.cycles.use_denoising=True
sc.render.resolution_x=1280; sc.render.resolution_y=720; sc.render.resolution_percentage=int(os.environ.get('PCT','80'))
sc.render.image_settings.file_format='JPEG'; sc.render.image_settings.quality=90
sc.render.threads_mode='FIXED'; sc.render.threads=4
for c in os.environ.get('ONLY',n+',WA2_CAM_eye_richardson_west_walk_from_N,WA2_CAM_oblique_richardson_west_walks_from_SW,WA2_CAM_eye_richardson_west_walk_from_W').split(','):
    sc.camera=O[c]; fp=f'{R}/renders/wip/{ts}_{c}_{suf}.jpg'; sc.render.filepath=fp
    bpy.ops.render.render(write_still=True); print('DONE',fp,datetime.now().strftime('%H:%M:%S'),flush=True)
print('EXIT',flush=True)
