import bpy, os, numpy as np
from mathutils import Vector
from datetime import datetime
from mathutils.bvhtree import BVHTree
R='/workspace/nj-scenes/montclair-state'; os.chdir(R)
O=bpy.data.objects; sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
def bvh(o):
    e=o.evaluated_get(dg); m=e.to_mesh(); b=BVHTree.FromPolygons([o.matrix_world@v.co for v in m.vertices],[tuple(p.vertices) for p in m.polygons]); e.to_mesh_clear(); return b
G=[bvh(O[n]) for n in O.keys() if O[n].type=='MESH' and n.startswith(('WV_stone','QW_DTM','Terrain_LiDAR','WT_rich','WU_rich','RZ2_','SA_ground','WF_east','QS_footway'))]
def gz(x,y):
    z=[h[0].z for b in G for h in [b.ray_cast(Vector((x,y,500)),Vector((0,0,-1)))] if h[0] is not None]; return max(z) if z else 136.3
def wpts(n,box):
    o=O[n]; P=np.array([(o.matrix_world@v.co)[:2] for v in o.data.vertices]); m=(P[:,0]>=box[0])&(P[:,0]<=box[1])&(P[:,1]>=box[2])&(P[:,1]<=box[3]); return P[m]
def at(P,key,val):
    i=np.argmin(np.abs(P[:,key]-val)); return P[i]
def mk(n,P,T,lens):
    cam=O.get(n) or bpy.data.objects.new(n,bpy.data.cameras.new(n))
    if n not in sc.collection.all_objects: O['WA2_CAM_closeup_richardson_west_walk_edge'].users_collection[0].objects.link(cam)
    cam.location=P; cam.data.lens=lens; cam.data.clip_start=.1; cam.data.clip_end=5000
    cam.rotation_euler=(T-P).to_track_quat('-Z','Y').to_euler(); print('CAM',n,tuple(round(c,2) for c in P),flush=True)
A=wpts('QS_footway_313027436_UNVERIFIED',(66,100,288,312)); a1=at(A,0,97); a2=at(A,0,74); a3=at(A,0,86)
mk('WF_CAM_eye_436_east_run_from_E',Vector((a1[0]+2,a1[1]-2.5,gz(a1[0]+2,a1[1]-2.5)+1.6)),Vector((a2[0],a2[1],gz(*a2)+0.3)),30)
mk('WF_CAM_closeup_436_east_edge',Vector((a3[0]+1.5,a3[1]-3.0,gz(a3[0]+1.5,a3[1]-3.0)+1.1)),Vector((a3[0]-0.8,a3[1],gz(*a3))),28)
B=wpts('QS_footway_313027428_UNVERIFIED',(28,52,250,325)); b1=at(B,1,B[:,1].min()+3); b2=at(B,1,B[:,1].min()+30)
mk('WF_CAM_eye_428_430_from_S',Vector((b1[0]+2.5,b1[1]-2,gz(b1[0]+2.5,b1[1]-2)+1.6)),Vector((b2[0],b2[1],gz(*b2)+0.3)),30)
if os.environ.get('SAVECAM')=='1': bpy.ops.wm.save_mainfile(); print('SAVED',len(O),flush=True)
ts=datetime.now().strftime('%Y%m%d-%H%M'); suf=os.environ.get('SUF','wf')
sc.render.engine='CYCLES'; sc.cycles.device='CPU'; sc.cycles.samples=int(os.environ.get('SAMP','24')); sc.cycles.use_denoising=True
sc.render.resolution_x=1280; sc.render.resolution_y=720; sc.render.resolution_percentage=int(os.environ.get('PCT','80'))
sc.render.image_settings.file_format='JPEG'; sc.render.image_settings.quality=90
sc.render.threads_mode='FIXED'; sc.render.threads=4
for c in os.environ.get('ONLY','WA2_CAM_oblique_richardson_west_walks_from_SW,WF_CAM_eye_436_east_run_from_E,WF_CAM_eye_428_430_from_S,WF_CAM_closeup_436_east_edge').split(','):
    sc.camera=O[c]; fp=f'{R}/renders/wip/{ts}_{c}_{suf}.jpg'; sc.render.filepath=fp
    bpy.ops.render.render(write_still=True); print('DONE',fp,datetime.now().strftime('%H:%M:%S'),flush=True)
print('EXIT',flush=True)
