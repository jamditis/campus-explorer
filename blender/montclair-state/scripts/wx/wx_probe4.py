import bpy, json, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
O=bpy.data.objects
exec(open('/workspace/nj-scenes/montclair-state/scripts/wx/wx_common.py').read())
ALL=dict(SB); ALL.update({n:bv(n) for n in G})
for n in ['TR_Stone_window_sills_UNVERIFIED','QY_walk_junction_wear_decals_UNVERIFIED']: ALL[n]=bv(n)
# along y, step x from west to wall; print the top obj/z at 0.1m steps within 1.5 m of wall
for y in np.arange(272,292,0.5):
    xs=np.arange(130,148,0.05); wall=None
    for x in xs:
        if inside(x,y): wall=x;break
    if wall is None: continue
    row=[]
    for dx in (1.5,1.0,0.6,0.4,0.25,0.15,0.08,0.03):
        x=wall-dx; best=None
        for n,b in ALL.items():
            r=b.ray_cast(Vector((x,y,400)),Vector((0,0,-1)))
            if r[0] is not None and (best is None or r[0].z>best[1]): best=(n[:6],round(r[0].z,2))
        row.append(f'{dx}:{best[0]}{best[1]}' if best else f'{dx}:-')
    print(round(y,1),round(wall,2),' '.join(row),flush=True)
