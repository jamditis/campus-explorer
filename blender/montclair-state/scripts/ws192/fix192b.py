# ws192b: dark notch at the W end of the WS191c strip-back lawn fillet (W eye view 20261116-1740). probe192e.out: at x -303.8,
# y -236.2 the fillet sits at 118.0 (-0.31 rel 118) while the ground/apron 0.2 m W is -0.55/-0.57 -> a 0.24 m exposed side face.
# Fix: taper the fillet's westernmost column: its t>0 verts drop to 1.5 cm under the adjacent ground (WS163 patch / WS162 apron /
# WS163 aisle top, max), so the W boundary dives under the lawn instead of standing as a wall; the strip-edge row (t=0) is kept.
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
def _b192b(o):
    M=o.matrix_world; return BVHTree.FromPolygons([M@v.co for v in o.data.vertices],[p.vertices[:] for p in o.data.polygons])
F192b=[o for o in bpy.data.objects if o.name.startswith('WS191c_Lot3_S_strip_back_lawn_fillet')][0]
G192b=[_b192b(o) for o in bpy.data.objects if o.name.startswith(('WS163_ground_patch_W_of_WS110','WS162_Lot3_S_end_apron_feather','WS163_Lot3_aisle_S_drive'))]
def gz192b(x,y):
    zs=[h[0].z for t in G192b for h in [t.ray_cast(Vector((x,y,300)),Vector((0,0,-1)))] if h[0]]
    return max(zs) if zs else None
vs=F192b.data.vertices; xmin=min(v.co.x for v in vs)
col=[v for v in vs if abs(v.co.x-xmin)<0.01]; ymax=max(v.co.y for v in col); n=0
for v in col:
    if v.co.y<ymax-0.01:
        g=gz192b(v.co.x-0.15,v.co.y)
        if g is not None and v.co.z>g-0.015: v.co.z=g-0.015; n+=1
# second column eases halfway to keep the slope smooth
xs=sorted(set(round(v.co.x,3) for v in vs)); x2=xs[1] if len(xs)>1 else None
m=0
if x2 is not None:
    for v in vs:
        if abs(v.co.x-x2)<0.01 and v.co.y<ymax-0.01:
            g=gz192b(v.co.x-0.15,v.co.y)
            if g is not None and v.co.z>g+0.02: v.co.z=0.5*(v.co.z+g); m+=1
F192b.data.update()
print('FIX192B xmin',round(xmin,2),'col1 lowered',n,'col2 eased',m,flush=True)
