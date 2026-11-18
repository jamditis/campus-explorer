"""wa renders: Cycles CPU low spp. CAMS env comma list; TESTCAM='x,y,z,tx,ty,tz,lens' makes a temp cam (not saved)."""
import bpy, os, math
from mathutils import Vector
from datetime import datetime
ts = os.environ.get('FORCE_TS') or datetime.now().strftime('%Y%m%d-%H%M')
OUT = os.environ.get('OUTDIR','/workspace/nj-scenes/montclair-state/renders/wip')
os.makedirs(OUT, exist_ok=True)
sc = bpy.context.scene
cams = [c for c in os.environ.get('CAMS','').split(',') if c]
tc = os.environ.get('TESTCAM')
if tc:
    v=[float(a) for a in tc.split(',')]
    cd=bpy.data.cameras.new('WA_TEST'); cd.lens=v[6]; cd.clip_end=30000
    o=bpy.data.objects.new('WA_TESTCAM',cd); sc.collection.objects.link(o)
    o.location=v[:3]; d=Vector(v[3:6])-Vector(v[:3])
    o.rotation_euler=(math.pi/2+math.atan2(d.z,math.hypot(d.x,d.y)),0,math.atan2(d.y,d.x)-math.pi/2)
    cams=['WA_TESTCAM']
sc.render.engine='CYCLES'; sc.cycles.device='CPU'
sc.cycles.samples=int(os.environ.get('SAMPLES','24')); sc.cycles.use_denoising=True
sc.render.resolution_x=1280; sc.render.resolution_y=720
sc.render.resolution_percentage=int(os.environ.get('RESPCT','80'))
sc.render.image_settings.file_format='JPEG'; sc.render.image_settings.quality=90
sc.render.threads_mode='FIXED'; sc.render.threads=4
print('OBJS',len(bpy.data.objects),'TS',ts,flush=True)
suf=os.environ.get('SUFFIX','wa')
for name in cams:
    cam=bpy.data.objects.get(name)
    if not cam: print('MISSING',name,flush=True); continue
    sc.camera=cam
    fp=f'{OUT}/{ts}_{name}_{suf}.jpg'
    sc.render.filepath=fp
    bpy.ops.render.render(write_still=True)
    print('DONE',name,fp,flush=True)
