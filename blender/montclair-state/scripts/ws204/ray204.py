# ws204 camera-pixel object map (probe only, never saved). env: FILE CAM CULL GRID=nx,ny OUTN
import bpy, os, json
S='/workspace/nj-scenes/montclair-state/scripts/'
exec(open(S+'ws189/alloff189.py').read())
bpy.ops.wm.open_mainfile(filepath=os.environ['FILE'])
for f in os.environ.get('CHAIN','').split(): exec(open(S+f).read())
from mathutils import Vector
sc=bpy.context.scene
cx0,cx1,cy0,cy1=map(float,os.environ['CULL'].split(','))
for o in sc.objects:
    if o.type in ('CAMERA','LIGHT'): continue
    if o.name.startswith('Context_skirt') or o.name.startswith('BD_farfield'): o.hide_render=True; continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]; xs=[v.x for v in bb]; ys=[v.y for v in bb]
    if max(xs)<cx0 or min(xs)>cx1 or max(ys)<cy0 or min(ys)>cy1: o.hide_render=True
for o in sc.objects:
    if o.hide_render:
        try: o.hide_set(True)
        except Exception: pass
dg=bpy.context.evaluated_depsgraph_get()
c=[float(a) for a in os.environ['CAM'].split(',')]; cam=Vector(c[:3]); tgt=Vector(c[3:6]); fl=c[6]
q=(tgt-cam).to_track_quat('-Z','Y'); W,H=1280,720; sw=36.0; sh=sw*H/W
nx,ny=map(int,os.environ.get('GRID','40,22').split(','))
out=[]
for j in range(ny):
    for i in range(nx):
        px=(i+0.5)*W/nx; py=(j+0.5)*H/ny
        d=q@Vector(((px/W-0.5)*sw,(0.5-py/H)*sh,-fl)); d.normalize()
        r=sc.ray_cast(dg,cam,d)
        out.append([px,py,r[4].name if r[0] else None,list(r[1]) if r[0] else None,list(r[2]) if r[0] else None])
json.dump(out,open(os.environ['OUTN'],'w'))
print('RAY204 done',len(out),flush=True)
for l in open('/proc/self/status'):
    if l.startswith('VmHWM'): print('MEM',l.strip(),flush=True)
