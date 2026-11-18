# render wrapper: HARD-remove objects whose bbox lies outside LEAN=x0,x1,y0,y1 (render-only; never saved) then run render162.py
import bpy, os
from mathutils import Vector
x0,x1,y0,y1=map(float,os.environ['LEAN'].split(','))
rm=[]
for o in bpy.data.objects:
    if o.type in ('CAMERA','LIGHT','EMPTY') or o.name.startswith(('Terrain_LiDAR','Context_skirt')): continue
    try: bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    except Exception: continue
    xs=[v.x for v in bb]; ys=[v.y for v in bb]
    if max(xs)<x0 or min(xs)>x1 or max(ys)<y0 or min(ys)>y1: rm.append(o)
for o in rm: bpy.data.objects.remove(o,do_unlink=True)
print('LEAN removed',len(rm),'kept',len(bpy.data.objects),flush=True)
exec(compile(open('/workspace/nj-scenes/montclair-state/scripts/ws163/render163.py').read(),'render162','exec'))
