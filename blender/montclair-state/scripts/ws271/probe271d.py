# ws271 probe (no save): first-hit object per 1 m cell over the Sprague grandstand lawn window, modifiers ON for objects in the window.
import bpy, numpy as np
from mathutils import Vector
OB=bpy.data.objects; W=(-262,-222,-140,-108)
for o in OB:
    if o.type!='MESH': continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    if max(b.x for b in bb)>W[0] and min(b.x for b in bb)<W[1] and max(b.y for b in bb)>W[2] and min(b.y for b in bb)<W[3]:
        for m in o.modifiers: m.show_viewport=True
for o in OB:
    if o.hide_render: o.hide_viewport=True
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
H={}; rows=[]; Z=[]
for y in np.arange(W[3]-0.5,W[2],-1.0):
    r=[]
    for x in np.arange(W[0]+0.5,W[1],1.0):
        ok,loc,nor,idx,ob,mx=sc.ray_cast(dg,Vector((x,y,300)),Vector((0,0,-1)))
        n=ob.name if ok else '-'
        if n not in H: H[n]=chr(65+len(H)) if len(H)<26 else chr(97+len(H)-26)
        r.append(H[n]+('^' if ok and nor.z<0.97 else ' ')); Z.append(loc.z if ok else np.nan)
    rows.append(f'{y:7.1f} '+''.join(r))
np.save('/workspace/nj-scenes/montclair-state/scripts/ws271/probe271d_z.npy',np.array(Z).reshape(len(rows),-1))
for k,v in H.items(): print('P271D KEY',v,k,flush=True)
for r in rows: print('P271D',r)
for l in open('/proc/self/status'):
    if l.startswith('VmHWM'): print('P271D',l.strip())
raise SystemExit(0)
