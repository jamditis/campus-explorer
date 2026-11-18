# ws195 WIP renders: full scene (modifiers on), cameras placed by ground raycast + eye height
import bpy, os, math
from mathutils import Vector
sc=bpy.context.scene
cx0,cx1,cy0,cy1=map(float,os.environ.get('CULL','-420,-60,-260,60').split(','))
for o in sc.objects:
    if o.type in ('CAMERA','LIGHT') or o.name.startswith('Context_skirt') or o.name.startswith('BD_farfield'): continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]; xs=[v.x for v in bb]; ys=[v.y for v in bb]
    if max(xs)<cx0 or min(xs)>cx1 or max(ys)<cy0 or min(ys)>cy1: o.hide_render=True
for o in bpy.data.objects:
    if o.type=='LIGHT': o.hide_render = not o.name.endswith('GOLDEN')
if 'WP2_World_GOLDEN' in bpy.data.worlds: sc.world=bpy.data.worlds['WP2_World_GOLDEN']
from mathutils.bvhtree import BVHTree
GB=[]
for o in bpy.data.objects:
    if o.type=='MESH' and any(o.name.startswith(p) for p in ('WS74_cogen_lot_asphalt','WS75_sprague_lot_asphalt','WS76_accessible_lot_asphalt','WS80_sprague_lot_fill','WS79_lot_E_patch','WS77_lot_median')):
        mw=o.matrix_world; GB.append(BVHTree.FromPolygons([mw@v.co for v in o.data.vertices],[p.vertices[:] for p in o.data.polygons]))
def gz(x,y):
    zs=[h[0].z for h in (B.ray_cast(Vector((x,y,400)),Vector((0,0,-1))) for B in GB) if h[0]]
    return max(zs) if zs else 124.0
sc.render.engine='CYCLES'; sc.cycles.device='CPU'; sc.cycles.samples=int(os.environ.get('SAMP','16')); sc.cycles.use_denoising=True
sc.render.resolution_x=1280; sc.render.resolution_y=720; sc.render.resolution_percentage=int(os.environ.get('PCT','60'))
sc.render.image_settings.file_format='JPEG'; sc.render.image_settings.quality=88; sc.render.threads_mode='FIXED'; sc.render.threads=4
sc.render.use_simplify=True; sc.cycles.texture_limit_render='1024'
T=os.environ['T']; TAG=os.environ['TAG']
for spec in os.environ['CAMS'].split(';'):
    n,cx,cy,hc,tx,ty,ht,fl=spec.split(','); cx,cy,hc,tx,ty,ht,fl=map(float,(cx,cy,hc,tx,ty,ht,fl))
    cz=gz(cx,cy)+hc; tz=gz(tx,ty)+ht
    c=bpy.data.objects.new(n,bpy.data.cameras.new(n)); sc.collection.objects.link(c)
    c.location=(cx,cy,cz); c.data.lens=fl; c.data.clip_start=0.1; c.data.clip_end=3000
    c.rotation_euler=(Vector((tx,ty,tz))-Vector((cx,cy,cz))).to_track_quat('-Z','Y').to_euler(); sc.camera=c
    fp='/workspace/nj-scenes/montclair-state/renders/%s/%s_%s_%s.jpg'%(os.environ.get('DIR','wip'),T,n,TAG); sc.render.filepath=fp
    bpy.ops.render.render(write_still=True); print('WROTE',fp,'camz %.2f'%cz,flush=True)
for l in open('/proc/self/status'):
    if l.startswith('VmHWM'): print('MEM195',l.strip(),flush=True)
