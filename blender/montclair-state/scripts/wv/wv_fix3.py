"""wv fix3 (review): shared edges (WU|WV at x=120, WV|WN/WO at x=155) are not patch ends, so the
skirt may dip fully there: recompute *_in on WV, WU, WN, WO excluding shared-edge verts from the
boundary-distance set (open-edge gate unchanged). Report skirt poke on WU/WV/WN/WO near the joints."""
import bpy, json, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree
R='/workspace/nj-scenes/montclair-state'
O=bpy.data.objects; sk=O['Context_skirt_3DEP_ortho_4km']
def ss(t):
    t=min(max(t,0.0),1.0); return t*t*(3-2*t)
def bvh(o):
    dg=bpy.context.evaluated_depsgraph_get(); e=o.evaluated_get(dg); m=e.to_mesh(); b=BVHTree.FromPolygons([o.matrix_world@v.co for v in m.vertices],[tuple(p.vertices) for p in m.polygons]); e.to_mesh_clear(); return b
def hz(b,x,y):
    h=b.ray_cast(Vector((x,y,500)),Vector((0,0,-1))); return h[0].z if h[0] is not None else None
P={'WV':('WV_stone_west_LiDAR_patch_UNVERIFIED','wv_in',[120.0,155.0]),
   'WU':('WU_richardson_reid_LiDAR_patch_UNVERIFIED','wu_in',[120.0]),
   'WN':('WN_south_wood_LiDAR_patch_ext_UNVERIFIED',None,[155.0]),
   'WO':('WO_gully_head_LiDAR_patch_UNVERIFIED',None,[155.0])}
rep={}
def poke(tag,box):
    BS=bvh(sk); out={}
    for k,(n,_,_) in P.items():
        B=bvh(O[n]); c=0; mx=0.0
        for x in np.arange(box[0]+0.25,box[1],0.5):
            for y in np.arange(box[2]+0.25,box[3],0.5):
                h=hz(B,x,y); s=hz(BS,x,y)
                if h is not None and s is not None and s>h-0.003: c+=1; mx=max(mx,s-h)
        out[k]=[c,round(mx,3)]
    rep['poke_'+tag]=out; print('POKE',tag,out,flush=True)
poke('before_x116_124',(116,124,245,320)); poke('before_x151_159',(151,159,228,320))
for k,(n,an,xs) in P.items():
    o=O[n]; me=o.data; mw=o.matrix_world
    if an is None:
        cands=[a.name for a in me.attributes if a.name.endswith('_in') and a.domain=='POINT']
        rep['attrs_'+k]=cands
        if not cands: continue
        an=cands[0]
    a=me.attributes.get(an)
    if a is None: continue
    cnt={}
    for p in me.polygons:
        for ek in p.edge_keys: cnt[ek]=cnt.get(ek,0)+1
    bv=set()
    for ek,c in cnt.items():
        if c==1: bv.update(ek)
    keep=[i for i in bv if not any(abs((mw@me.vertices[i].co).x-X)<0.02 and 245<= (mw@me.vertices[i].co).y <=320 for X in xs)]
    old=np.array([d.value for d in a.data])
    # recover open-gate factor: new = min(old_scale*ss(d_new/0.8), gate) -> approximate gate as old/0.40/ss(d_old/0.8)
    kt_old=KDTree(len(bv)); [kt_old.insert(me.vertices[i].co,i) for i in bv]; kt_old.balance()
    kt=KDTree(max(1,len(keep))); [kt.insert(me.vertices[i].co,i) for i in keep]; kt.balance()
    scale=max(old.max(),1e-6)
    n=0
    for v in me.vertices:
        c=mw@v.co
        if not any(abs(c.x-X)<12 for X in xs) or not (240<=c.y<=325): continue
        _,_,do=kt_old.find(v.co); _,_,dn=kt.find(v.co)
        wo=ss(do/0.8); wn=ss(dn/0.8)
        if wn<=wo+1e-4: continue
        gate=old[v.index]/scale/wo if wo>1e-3 else 1.0
        gate=min(1.0,gate)
        nv=scale*min(wn,gate) if wo>1e-3 else scale*wn*(1.0 if old[v.index]>0 or True else 0)
        if nv>old[v.index]+1e-4: a.data[v.index].value=nv; n+=1
    me.update(); rep['raised_in_'+k]=[an,n,round(float(scale),3),len(bv),len(keep)]; print('IN',k,an,n,len(bv),len(keep),flush=True)
bpy.context.view_layer.update()
poke('after_x116_124',(116,124,245,320)); poke('after_x151_159',(151,159,228,320))
r=json.load(open(f'{R}/data/wv/fix_report.json')); r['fix3']=rep
json.dump(r,open(f'{R}/data/wv/fix_report.json','w'),indent=1)
if 'NOSAVE' not in __import__('os').environ: bpy.ops.wm.save_mainfile(); print('SAVED',flush=True)
