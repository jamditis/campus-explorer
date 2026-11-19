# ws232 probe d: lifted overlay verts (ws232a) vs evaluated Footpaths/Roads surface and evaluated top ground at the same xy
import bpy,sys,os,json,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
M='/workspace/nj-scenes/montclair-state/'
exec(open(M+'scripts/ws232/probe232b.py').read().split("out={}; rep={}")[0].replace("os.environ.get('PF','montclair_state.blend')","os.environ.get('PF','montclair_state_ws232a.blend')"))
import os as _o
for n in OV:
    if n not in O: continue
    o=O[n]; W=o.matrix_world; s=[]
    for v in o.data.vertices:
        w=W@v.co
        if not (112<w.x<152 and 182<w.y<252): continue
        e=[PE[p].ray_cast(Vector((w.x,w.y,400)),Vector((0,0,-1)))[0] for p in PV]; e=[h.z for h in e if h is not None]
        g=top(GB,w.x,w.y)
        s.append((round(w.z-max(e),2) if e else None,round(w.z-g,2) if g is not None else None,round(w.x,1),round(w.y,1)))
    sp=[t for t in s if t[0] is not None]; sg=[t for t in s if t[1] is not None]
    print('P232D',n,'verts',len(s),'onpave',len(sp),'z-pave q',[round(float(q),2) for q in np.percentile([t[0] for t in sp],[0,10,50,90,100])] if sp else None,'z-ground q',[round(float(q),2) for q in np.percentile([t[1] for t in sg],[0,10,50,90,100])] if sg else None,'worstg',sorted(sg,key=lambda t:t[1])[:2],flush=True)
os._exit(0)
