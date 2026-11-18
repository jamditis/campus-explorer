# ws73b: WS72b slab road-side edge was row-smoothed and pulled off the curb back on the bend -> grass/terrain slivers (the "stepped notches").
# Snap its road-side edge (top+bottom verts) to the WS27 curb_left back line, 1 cm over the curb top edge (slab is +1 cm above curb top, no z-fight).
import bpy,os
from collections import defaultdict
c=bpy.data.objects['WS27_CollegeAve_curb_left_UNVERIFIED']; V=c.data.vertices
back=sorted([(V[6*r+4].co.x,V[6*r+4].co.y) for r in range(len(V)//6) if -230<V[6*r].co.x<-190 and V[6*r].co.y>-95])
def by(x):
    for (x0,y0),(x1,y1) in zip(back,back[1:]):
        if x0<=x<=x1: return y0+(y1-y0)*(x-x0)/(x1-x0 if x1!=x0 else 1)
    return None
s=bpy.data.objects['WS72b_Kasser_S_sidewalk_east_to_Cole_UNVERIFIED_width']; me=s.data
g=defaultdict(list)
for v in me.vertices: g[round(v.co.x,2)].append(v)
mx=0;n=0
for x,vs in g.items():
    y0=min(v.co.y for v in vs); edge=[v for v in vs if abs(v.co.y-y0)<1e-4]
    b=by(x)
    if b is None: continue
    ny=b-0.01
    if ny<y0+0.001:
        for v in edge: mx=max(mx,y0-ny); v.co.y=ny; n+=1
me.update(); print('W73b snapped verts',n,'max shift',round(mx,3),flush=True)
if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('W73b SAVED',flush=True)
