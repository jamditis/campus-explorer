# ws232 probe e (from probe d): snap targets = evaluated paving top + decal offset for the lifted overlay verts in ws232a; lifted overlay verts (ws232a) vs evaluated Footpaths/Roads surface and evaluated top ground at the same xy
import bpy,sys,os,json,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
M='/workspace/nj-scenes/montclair-state/'
exec(open(M+'scripts/ws232/probe232b.py').read().split("out={}; rep={}")[0].replace("os.environ.get('PF','montclair_state.blend')","os.environ.get('PF','montclair_state_ws232a.blend')"))
D={'OY_walk_panel_tone_CELS_Calcia_UNVERIFIED':0.008,'OY_walk_scoring_joints_CELS_Calcia_UNVERIFIED':0.012,'OX_CELS_walk_scoring_joints_UNVERIFIED':0.012}
out={}
for n,dl in D.items():
    o=O[n]; W=o.matrix_world; r={}
    for v in o.data.vertices:
        w=W@v.co
        if not (112<w.x<152 and 182<w.y<252): continue
        e=[PE[p].ray_cast(Vector((w.x,w.y,400)),Vector((0,0,-1)))[0] for p in PV]; e=[h.z for h in e if h is not None]
        if e: r[v.index]=round(max(e)+dl,4)
    out[n]=r; print('P232E',n,len(r),flush=True)
json.dump(out,open(M+'scripts/ws232/snap232_targets.json','w'))
os._exit(0)
