# list other objects whose world bbox touches the WS110 S band (t 1..196, off -4..+1) — for the record (LOG), no edits
import bpy, numpy as np
from mathutils import Vector
A=np.array([-268.8,-262.9]); N=np.array([0.236,1.0]); N/=np.linalg.norm(N); T=np.array([N[1],-N[0]])
pts=np.array([A+N*(-0.01446*t-11.028+o)+T*t for t in np.linspace(1,196,80) for o in (-4,-1.5,1)])
mine=('WS110_NormalAve','WS110_ground_patch','WS113_paving','WS174_junction','WS163_','WS172_','WS175_')
for o in bpy.data.objects:
    if o.type!='MESH' or o.name.startswith(mine): continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]; xs=[c.x for c in bb]; ys=[c.y for c in bb]; zs=[c.z for c in bb]
    if max(xs)-min(xs)>400: continue
    k=(pts[:,0]>=min(xs))&(pts[:,0]<=max(xs))&(pts[:,1]>=min(ys))&(pts[:,1]<=max(ys))
    if k.any() and max(zs)>110: print('BAND175',o.name[:80],'hide_render',o.hide_render,'z %.1f..%.1f'%(min(zs),max(zs)),flush=True)
