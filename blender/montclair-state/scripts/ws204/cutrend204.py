# ws189 probe render: all modifiers off (alloff189), skirt/farfield hidden, tight CULL, camera = W eye (z from env)
import bpy, os, math
from mathutils import Vector
sc=bpy.context.scene
cx0,cx1,cy0,cy1=map(float,os.environ.get('CULL','-345,-300,-245,-215').split(','))
HIDE=os.environ.get('HIDE','Context_skirt|BD_farfield').split('|')
for o in sc.objects:
    if o.type in ('CAMERA','LIGHT'): continue
    if any(h and o.name.startswith(h) for h in HIDE): o.hide_render=True; continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]; xs=[v.x for v in bb]; ys=[v.y for v in bb]
    if max(xs)<cx0 or min(xs)>cx1 or max(ys)<cy0 or min(ys)>cy1: o.hide_render=True
for o in bpy.data.objects:
    if o.type=='LIGHT': o.hide_render = not o.name.endswith('GOLDEN')
if 'WP2_World_GOLDEN' in bpy.data.worlds: sc.world=bpy.data.worlds['WP2_World_GOLDEN']
cx,cy,cz,tx,ty,tz,fl=[float(a) for a in os.environ['CAM'].split(',')]
c=bpy.data.objects.new('C189',bpy.data.cameras.new('C189')); sc.collection.objects.link(c)
c.location=(cx,cy,cz); c.data.lens=fl; c.data.clip_start=0.1; c.data.clip_end=3000
c.rotation_euler=(Vector((tx,ty,tz))-Vector((cx,cy,cz))).to_track_quat('-Z','Y').to_euler(); sc.camera=c
sr=os.environ.get('SUNROT')
if sr:
    for nd in sc.world.node_tree.nodes:
        if nd.type=='TEX_SKY': print('SKY',nd.sun_rotation,nd.sun_elevation); nd.sun_rotation=float(sr)
sc.render.engine='CYCLES'; sc.cycles.device='CPU'; sc.cycles.samples=int(os.environ.get('SAMP','12')); sc.cycles.use_denoising=True
sc.render.resolution_x=1280; sc.render.resolution_y=720; sc.render.resolution_percentage=int(os.environ.get('PCT','60'))
sc.render.image_settings.file_format='JPEG'; sc.render.image_settings.quality=88; sc.render.threads_mode='FIXED'; sc.render.threads=4
sc.render.use_simplify=True; sc.cycles.texture_limit_render=os.environ.get('TEXLIM','1024')
fp=os.environ['OUTF']; sc.render.filepath=fp; bpy.ops.render.render(write_still=True); print('WROTE',fp,flush=True)
for l in open('/proc/self/status'):
    if l.startswith('VmHWM'): print('MEM189',l.strip(),flush=True)
