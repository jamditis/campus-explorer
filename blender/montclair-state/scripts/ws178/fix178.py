# UNIFY #86 (ws178): residual lawn-over-paving found by scripts/ws178/bury178.py after the ws177 chain:
# WS163 Lot 3 aisle S drive (ground patch W of WS110, 4 verts up to 0.33 m), WS163 S walk-back lip (1 vert 0.18 m),
# WS134 Freeman block patch over WS110 Normal Ave E end (5 verts up to 0.14 m). Clamp ground verts inside a paving footprint
# to paving top -0.05 (curb/verge -0.20); verts within 0.4 m outside a footprint only if the clamp is <= 0.10 m (no trenches).
import bpy, numpy as np, re
from mathutils.bvhtree import BVHTree
from mathutils import Vector
OB=bpy.data.objects
pav=[o for o in OB if o.type=='MESH' and re.search(r'carriageway|curb|kerb|sidewalk|walk|road|drive|apron|concrete|asphalt|paving|crosswalk',o.name,re.I) and 'proxy' not in o.name and not re.search(r'ground|lawn|grass|verge|lip',o.name,re.I) and o.name.startswith(('WS110','WS163','WS166','WS170','WS172','WS173','WS174','WS175'))]
GN=('WS163_walk_back_lawn_lip_S','WS163_ground_patch_W_of_WS110','WS134_ground_patch')
def top(x,y,z,trees):
    best=None;nm=None
    for o,tr in trees:
        Mi=o.matrix_world.inverted(); pl=Mi@Vector((x,y,z+3.0)); dl=(Mi.to_3x3()@Vector((0,0,-1))).normalized()
        h=tr.ray_cast(pl,dl,6.0)
        if h[0] is not None:
            hz=(o.matrix_world@h[0]).z
            if best is None or hz>best: best=hz;nm=o.name
    return best,nm
for it in range(2):
    dg=bpy.context.evaluated_depsgraph_get()
    trees=[(o,BVHTree.FromObject(o,dg)) for o in pav]
    for g in [o for o in OB if o.type=='MESH' and o.name.startswith(GN)]:
        ge=g.evaluated_get(dg); me=ge.to_mesh(); M=g.matrix_world
        if len(me.vertices)!=len(g.data.vertices): print('FIX178 topology differs, skip',g.name); ge.to_mesh_clear(); continue
        W=np.array([(M@v.co)[:] for v in me.vertices]); ge.to_mesh_clear(); n=0; mx=0
        for i,w in enumerate(W):
            z,nm=top(w[0],w[1],w[2],trees); lim=None
            if z is not None:
                lim=z-(0.20 if ('curb' in nm.lower() or 'kerb' in nm.lower()) else (0.02 if 'lawn_lip' in g.name else 0.05))
            elif 'lawn_lip' in g.name: lim=None
            else:
                zs=[top(w[0]+dx,w[1]+dy,w[2],trees)[0] for dx,dy in ((0.4,0),(-0.4,0),(0,0.4),(0,-0.4))]
                zs=[q for q in zs if q is not None]
                if zs and w[2]>min(zs)-0.05 and w[2]-(min(zs)-0.05)<=0.10: lim=min(zs)-0.05
            if lim is not None and w[2]>lim:
                dz=lim-w[2]; g.data.vertices[i].co.z+=dz/g.matrix_world.to_scale().z; n+=1; mx=min(mx,dz)
        g.data.update(); print('FIX178 pass %d %s lowered %d (max %.2f)'%(it,g.name[:40],n,mx),flush=True)
print('FIX178 done',flush=True)
