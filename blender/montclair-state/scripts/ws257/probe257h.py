# ws257 read-only UNIFY #10: per x (1 m), the WS110 patch's evaluated S edge (southmost y with patch, its z) and the evaluated
# skirt z on a 1 m grid from that edge 30 m south -> json for f257c (merge208 runs with modifiers off, so this is precomputed).
import sys; sys.stdout.reconfigure(line_buffering=True)
import bpy, os, json, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
MS='/workspace/nj-scenes/montclair-state/'
P='WS110_ground_patch_S_of_y-238_DTM2023_1m_lawn_UNVERIFIED'; S='Context_skirt_3DEP_ortho_4km'
OTH=['WS172_frontyards_S_of_NormalAve_W_DTM2023_J5D5','WS110_NormalAve_sidewalk_ws85prep_ortho2020_UNVERIFIED','WS175_WS110_walk_back_lawn_lip_S_UNIFY80']
with bpy.data.libraries.load(MS+'montclair_state.blend') as (a,b): b.objects=[n for n in [P,S]+OTH if n in a.objects]
for o in b.objects: bpy.context.scene.collection.objects.link(o)
dg=bpy.context.evaluated_depsgraph_get()
X0,X1,Y0,Y1=-300,-160,-345,-280
def bv(o):
    me=o.evaluated_get(dg).to_mesh(); M=o.matrix_world; vs=[M@v.co for v in me.vertices]
    ps=[p.vertices[:] for p in me.polygons if any(X0<vs[i].x<X1 and Y0<vs[i].y<Y1 for i in p.vertices)]
    return BVHTree.FromPolygons(vs,ps) if ps else None
PB=bv(bpy.data.objects[P]); SB=bv(bpy.data.objects[S]); OB={n:bv(bpy.data.objects[n]) for n in OTH if n in bpy.data.objects}
def z(bt,x,y):
    h=bt.ray_cast(Vector((x,y,400)),Vector((0,0,-1)),600); return h[0].z if h[0] else None
out={}
for x in np.arange(-290.0,-160.0,1.0):
    ye=None
    for y in np.arange(-285.0,-305.01,-0.1):
        if z(PB,x,y) is not None: ye=y
        elif ye is not None and y<ye-0.5: break
    if ye is None: continue
    ze=z(PB,x,ye)
    oth={n[:12]:z(t,x,ye-0.4) for n,t in OB.items() if t and z(t,x,ye-0.4) is not None}
    sk=[z(SB,x,ye-d) for d in range(0,31)]
    out[str(x)]={'ye':round(float(ye),2),'ze':ze,'sk':sk,'oth':oth}
    if int(x)%10==0: print('P257H x',x,'edge y %.1f z %.2f'%(ye,ze),'skirt@0,5,10,20,30',[round(sk[d],2) if sk[d] else None for d in (0,5,10,20,30)],'others',{k:round(v,2) for k,v in oth.items()})
json.dump(out,open(MS+'scripts/ws257/edge257.json','w')); print('P257H columns',len(out))
os._exit(0)
