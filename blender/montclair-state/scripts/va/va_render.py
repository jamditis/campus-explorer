"""Render unchanged uy review cameras after session-va signage fit."""
import bpy, os
from datetime import datetime
D='/workspace/nj-scenes/montclair-state'
ts=datetime.now().strftime('%Y%m%d-%H%M')
open(D+'/data/va/wip_ts.txt','w').write(ts)
sc=bpy.context.scene
sc.render.engine='CYCLES'
sc.cycles.device='CPU'
sc.cycles.samples=int(os.environ.get('SAMPLES','40'))
sc.cycles.use_denoising=True
sc.render.resolution_x=1280; sc.render.resolution_y=720; sc.render.resolution_percentage=100
sc.render.image_settings.file_format='JPEG'; sc.render.image_settings.quality=92
sc.render.threads_mode='FIXED'; sc.render.threads=4
cams=os.environ.get('CAMS','UY_CAM_closeup_Freeman_N_lettering_terracotta,UY_CAM_oblique_Freeman_from_NW').split(',')
for name in cams:
    sc.camera=bpy.data.objects[name]
    path=D+'/renders/wip/'+ts+'_'+name+'_va.jpg'
    sc.render.filepath=path
    print('VA RENDER',path,flush=True)
    bpy.ops.render.render(write_still=True)
    print('VA DONE',path,os.path.getsize(path),flush=True)
