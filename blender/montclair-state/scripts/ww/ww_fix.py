"""ww fix: ease the Stone Street verge. 2020 ortho (north/data/ortho2020_north.jpg, 0.405 m/px) shows lawn
running straight onto the asphalt on the west/lawn side with no distinct kerb line -> no kerb modelled.
Raise-only: ground verts BESIDE the road slab (not under any road/walk slab) within D_FULL of the road's top
boundary go to slab top -1 cm, blending back to their current z by D_OUT. Verts under any slab untouched
(stay walk -3 cm). Only top-most ground verts are moved. Measure exposure + slab pokes before/after;
any vert whose raise creates a poke is backed off. Grass re-snapped."""
import bpy, json, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree
R='/workspace/nj-scenes/montclair-state'; O=bpy.data.objects
ROADS=['QS_service_546643370_UNVERIFIED','QW_service_546643370_ext_UNVERIFIED']
WALKS=['QS_footway_546643369_UNVERIFIED','QT_soil_edge_546643369_UNVERIFIED','TR_footway_546643369_S_gap_UNVERIFIED','SG_QuadRoad_full_313028548_549_UNVERIFIED','QW_footway_546643369_ext_UNVERIFIED']
GRD=['WV_stone_west_LiDAR_patch_UNVERIFIED','QW_DTM_north_edge_ramp_UNVERIFIED','WF_east_dorm_LiDAR_terrain_patch_UNVERIFIED','WU_richardson_reid_LiDAR_patch_UNVERIFIED','WN_south_wood_LiDAR_patch_ext_UNVERIFIED','WO_gully_head_LiDAR_patch_UNVERIFIED']
MOVE=['WV_stone_west_LiDAR_patch_UNVERIFIED','QW_DTM_north_edge_ramp_UNVERIFIED','WF_east_dorm_LiDAR_terrain_patch_UNVERIFIED']
BX=(112,172,244,362); D_FULL=1.0; D_OUT=2.2; LIFT=0.025; CAP=0.40
dg=bpy.context.evaluated_depsgraph_get()
def mesh(o,ev=True):
    if ev:
        e=o.evaluated_get(dg); m=e.to_mesh()
    else: m=o.data
    V=[o.matrix_world@v.co for v in m.vertices]; P=[tuple(p.vertices) for p in m.polygons]; N=[(o.matrix_world.to_3x3()@p.normal).normalized() for p in m.polygons]
    if ev: e.to_mesh_clear()
    return V,P,N
def hz(b,x,y):
    h=b.ray_cast(Vector((x,y,500)),Vector((0,0,-1))); return h[0].z if h[0] is not None else None
RB={n:BVHTree.FromPolygons(*mesh(O[n])[:2]) for n in ROADS}
WB={n:BVHTree.FromPolygons(*mesh(O[n])[:2]) for n in WALKS if O.get(n)}
SB=dict(RB); SB.update(WB)
def stop(x,y,bs=SB):
    z=[hz(b,x,y) for b in bs.values()]; z=[q for q in z if q is not None]; return max(z) if z else None
# road top boundary samples
pts=[]
for rn in ROADS:
    V,P,N=mesh(O[rn]); from collections import Counter; ec=Counter()
    for p,q in zip(P,N):
        if q.z<0.5: continue
        for i in range(len(p)): ec[tuple(sorted((p[i],p[(i+1)%len(p)])))]+=1
    for (a,b),c in ec.items():
        if c!=1: continue
        A,B=V[a],V[b]; L=(B-A).length; n=max(1,int(L/0.1))
        for k in range(n+1): pts.append(A+(B-A)*(k/n))
kd=KDTree(len(pts))
for i,p in enumerate(pts): kd.insert(Vector((p.x,p.y,0)),i)
kd.balance()
def gbvh(): return {n:BVHTree.FromPolygons(*mesh(O[n])[:2]) for n in GRD if O.get(n)}
def gtop(GB,x,y):
    z=[hz(b,x,y) for b in GB.values()]; z=[q for q in z if q is not None]; return max(z) if z else None
def exposure(tag):
    GB=gbvh(); ex=[]
    for i in range(0,len(pts),5):
        p=pts[i]
        # outward direction: probe 8 dirs at 0.25 m, take those off-slab
        for ang in np.linspace(0,2*np.pi,8,endpoint=False):
            x=p.x+0.25*np.cos(ang); y=p.y+0.25*np.sin(ang)
            if stop(x,y) is not None: continue
            g=gtop(GB,x,y)
            if g is not None: ex.append(p.z-g)
            break
    ex=np.array(ex); r=dict(n=len(ex),p50=round(float(np.median(ex)),3),p90=round(float(np.percentile(ex,90)),3),max=round(float(ex.max()),3),n_gt5=int((ex>0.05).sum()),n_gt3=int((ex>0.03).sum()),n_lt_m3=int((ex<-0.03).sum()))
    print('EXPOSURE',tag,r,flush=True); return r
def pokes(tag):
    GB=gbvh(); c=0; tot=0; mx=0; where={}
    for x in np.arange(BX[0],BX[1],0.25):
        for y in np.arange(BX[2],BX[3],0.25):
            s=stop(x,y)
            if s is None: continue
            tot+=1; g=gtop(GB,x,y)
            if g is not None and g>s-0.005:
                c+=1; mx=max(mx,g-s); k=(int(x)//5*5,int(y)//5*5); where[k]=where.get(k,0)+1
    r=[c,tot,round(mx,3),sorted(where.items(),key=lambda t:-t[1])[:10]]; print('POKES',tag,r,flush=True); return r
rep={'exp_before':exposure('before'),'poke_before':pokes('before')}
GB0=gbvh(); moved={}
for n in MOVE:
    o=O[n]; me=o.data; mw=o.matrix_world; mi=mw.inverted()
    np.save(f'{R}/data/ww/{n[:12]}_pre_ww.npy',np.array([v.co[:] for v in me.vertices]))
    cnt=0; mx=0.0; lst=[]
    for v in me.vertices:
        c=mw@v.co
        if not (BX[0]<=c.x<=BX[1] and BX[2]<=c.y<=BX[3]): continue
        if stop(c.x,c.y) is not None: continue        # under a slab: stay tucked
        co,i,d=kd.find(Vector((c.x,c.y,0)))
        if d>D_OUT: continue
        g=gtop(GB0,c.x,c.y)
        if g is not None and c.z<g-0.05: continue      # buried under another ground sheet
        top=pts[i].z-LIFT
        s=0.0 if d<=D_FULL else (d-D_FULL)/(D_OUT-D_FULL); s=s*s*(3-2*s)
        t=top*(1-s)+c.z*s
        if t>c.z+0.002:
            dz=min(t-c.z,CAP); c.z+=dz; v.co=mi@c; cnt+=1; mx=max(mx,dz); lst.append(v.index)
    me.update(); moved[n]=lst; rep['raise_'+n[:12]]=[cnt,round(mx,3)]; print('RAISE',n[:12],cnt,round(mx,3),flush=True)
bpy.context.view_layer.update(); dg=bpy.context.evaluated_depsgraph_get()
rep['poke_after1']=pokes('after1')
# back off: any moved vert whose adjacent faces now poke a slab -> lower toward original in steps
for it in range(4):
    if rep.get('poke_after%d'%(it+1))[0]<=rep['poke_before'][0]: break
    GB=gbvh(); fixed=0
    for n in MOVE:
        o=O[n]; me=o.data; mw=o.matrix_world; mi=mw.inverted(); pre=np.load(f'{R}/data/ww/{n[:12]}_pre_ww.npy')
        ids=set(moved[n]); adj={}
        for p in me.polygons:
            vs=list(p.vertices)
            if ids.intersection(vs):
                cen=mw@p.center; s=stop(cen.x,cen.y)
                if s is not None and cen.z>s-0.005:
                    for vi in vs:
                        if vi in ids: adj[vi]=1
                # also check each vert-to-centre midpoints
                for vi in vs:
                    if vi not in ids: continue
                    q=(mw@me.vertices[vi].co+cen)/2; s=stop(q.x,q.y)
                    if s is not None and q.z>s-0.005: adj[vi]=1
        for vi in adj:
            v=me.vertices[vi]; v.co.z=(v.co.z+pre[vi][2])/2; fixed+=1
        me.update()
    bpy.context.view_layer.update(); dg=bpy.context.evaluated_depsgraph_get()
    print('BACKOFF',it,fixed,flush=True)
    rep['poke_after%d'%(it+2)]=pokes('after%d'%(it+2))
rep['exp_after']=exposure('after')
# grass reseat near roads
GB=gbvh()
for name in ('QS_Richardson_lawn_grass_points_UNVERIFIED','QV_Richardson_NW_lawn_grass_points_UNVERIFIED'):
    o=O.get(name)
    if not o: continue
    me=o.data; mw=o.matrix_world; mi=mw.inverted(); k=0; dn=0; mx=0.0
    np.save(f'{R}/data/ww/{name[:2]}_grass_pre_ww.npy',np.array([v.co[:] for v in me.vertices]))
    for v in me.vertices:
        c=mw@v.co
        if not (BX[0]<=c.x<=BX[1] and BX[2]<=c.y<=BX[3]): continue
        co,i,d=kd.find(Vector((c.x,c.y,0)))
        if d>D_OUT+0.6: continue
        g=gtop(GB,c.x,c.y)
        if g is None: continue
        if stop(c.x,c.y) is not None:
            if c.z>g-0.15: c.z=g-0.2; v.co=mi@c; dn+=1
            continue
        if abs(c.z-g)>0.01: mx=max(mx,abs(c.z-g)); c.z=g; v.co=mi@c; k+=1
    me.update(); rep['grass_'+name[:2]]=[k,dn,round(mx,3)]; print('GRASS',name[:2],k,dn,round(mx,3),flush=True)
json.dump(rep,open(f'{R}/data/ww/fix_report.json','w'),indent=1)
import sys
if '--save' in sys.argv:
    bpy.ops.wm.save_mainfile(); print('SAVED',len(bpy.data.objects),flush=True)
print('EXIT',flush=True)
