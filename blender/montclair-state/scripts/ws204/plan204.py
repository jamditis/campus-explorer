# ws204 plan-view top-object map (probe only). env: FILE BOX=x0,x1,y0,y1 STEP OUTN
import bpy, os, json
S='/workspace/nj-scenes/montclair-state/scripts/'
exec(open(S+'ws189/alloff189.py').read())
bpy.ops.wm.open_mainfile(filepath=os.environ['FILE'])
for f in os.environ.get('CHAIN','').split(): exec(open(S+f).read())
from mathutils import Vector
sc=bpy.context.scene
x0,x1,y0,y1=map(float,os.environ['BOX'].split(',')); st=float(os.environ.get('STEP','0.25'))
SKIP=('Context_skirt','BD_farfield','T_','Tree','MID_canopy')
for o in sc.objects:
    if o.type!='MESH' or o.name.startswith(SKIP) or o.hide_render:
        try: o.hide_set(True)
        except Exception: pass
        continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]; xs=[v.x for v in bb]; ys=[v.y for v in bb]; zs=[v.z for v in bb]
    if max(xs)<x0 or min(xs)>x1 or max(ys)<y0 or min(ys)>y1 or min(zs)>140:
        try: o.hide_set(True)
        except Exception: pass
dg=bpy.context.evaluated_depsgraph_get(); out=[]
nx=int(round((x1-x0)/st)); ny=int(round((y1-y0)/st))
for j in range(ny):
    for i in range(nx):
        x=x0+(i+0.5)*st; y=y0+(j+0.5)*st
        r=sc.ray_cast(dg,Vector((x,y,140.0)),Vector((0,0,-1)))
        out.append([x,y,r[4].name if r[0] else None,r[1].z if r[0] else None])
json.dump({'nx':nx,'ny':ny,'box':[x0,x1,y0,y1],'st':st,'d':out},open(os.environ['OUTN'],'w'))
print('PLAN204 done',nx,ny,flush=True)
for l in open('/proc/self/status'):
    if l.startswith('VmHWM'): print('MEM',l.strip(),flush=True)
