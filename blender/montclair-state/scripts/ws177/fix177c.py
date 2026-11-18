# UNIFY #85 (ws177): WS110 ground patch (after its GN paving_edge_grade) sits 0.1-0.33 m ABOVE Normal Ave paving at t 80..140
# (161 verts; the WS113 proxy has no N-side/E coverage there) -> lawn buries the road. Lower base verts so the evaluated
# ground is >= 5 cm under the paving top everywhere in the paving footprint (+0.4 m margin, 5 cm under the nearest paving top);
# under the curb and grass verge the ground goes to road level -5 cm (curb top -0.20) so facets cannot poke out in the gutter.
import bpy, numpy as np
from mathutils.bvhtree import BVHTree
from mathutils import Vector
A=np.array([-268.8,-262.9]); N=np.array([0.236,1.0]); N/=np.linalg.norm(N); T=np.array([N[1],-N[0]])
OB=bpy.data.objects
pav=[o for o in OB if o.type=='MESH' and o.name.startswith(('WS110_NormalAve_carriageway','WS110_NormalAve_curb','WS110_NormalAve_sidewalk','WS110_NormalAve_verge'))]
def top(x,y,trees):
    best=None; HIT[0]=None
    for o,tr in trees:
        Mi=o.matrix_world.inverted(); pl=Mi@Vector((x,y,500.0)); dl=(Mi.to_3x3()@Vector((0,0,-1))).normalized()
        h=tr.ray_cast(pl,dl,1000)
        if h[0] is not None:
            z=(o.matrix_world@h[0]).z
            if best is None or z>best: best=z; HIT[0]=o.name
    return best
HIT=[None]
for it in range(2):
    dg=bpy.context.evaluated_depsgraph_get()
    trees=[(o,BVHTree.FromObject(o,dg)) for o in pav]
    for g in [o for o in OB if o.type=='MESH' and o.name.startswith(('WS110_ground_patch','WS138b_ground_fill','WS134_ground_patch','WS133b_ground_patch'))]:
        ge=g.evaluated_get(dg); me=ge.to_mesh(); M=g.matrix_world
        if len(me.vertices)!=len(g.data.vertices): print('FIX177C topology differs, skip',g.name); ge.to_mesh_clear(); continue
        W=np.array([(M@v.co)[:] for v in me.vertices]); ge.to_mesh_clear()
        d=W[:,:2]-A; t=d@T; s=d@N; n=0; mx=0
        for i in np.where((t>-5)&(t<200)&(s>-14.5)&(s<5))[0]:
            z=top(W[i,0],W[i,1],trees)
            if z is None:
                zs=[top(W[i,0]+dx,W[i,1]+dy,trees) for dx,dy in ((0.4,0),(-0.4,0),(0,0.4),(0,-0.4))]
                zs=[q for q in zs if q is not None]
                if not zs: continue
                z=min(zs); lim=z-0.05
            else:
                lim=z-0.05
                # under curb / grass verge: keep ground at road level -5 cm so 1 m ground facets never cross the curb face above the gutter
                if HIT[0] and ('curb' in HIT[0] or 'verge' in HIT[0]): lim=z-0.20
            if W[i,2]>lim:
                dz=lim-W[i,2]; g.data.vertices[i].co.z+=dz/g.matrix_world.to_scale().z; n+=1; mx=min(mx,dz)
        g.data.update(); print('FIX177C pass %d %s lowered %d (max %.2f)'%(it,g.name[:40],n,mx),flush=True)
print('FIX177C done',flush=True)
