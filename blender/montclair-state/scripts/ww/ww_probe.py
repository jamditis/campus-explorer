"""ww probe: exposed slab side along Stone Street (QS service + QW ext). For each boundary edge of the road
slab top, sample slab top z and ground z 0.25/0.5/1.0 m outward (perpendicular, away from slab interior);
skip points that land on another walk slab. Report exposure stats and lists of candidate ground verts."""
import bpy, json, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R='/workspace/nj-scenes/montclair-state'; O=bpy.data.objects
ROADS=['QS_service_546643370_UNVERIFIED','QW_service_546643370_ext_UNVERIFIED']
WALKS=['QS_footway_546643369_UNVERIFIED','QT_soil_edge_546643369_UNVERIFIED','TR_footway_546643369_S_gap_UNVERIFIED','SG_QuadRoad_full_313028548_549_UNVERIFIED','QW_footway_546643369_ext_UNVERIFIED']
GRD=['WV_stone_west_LiDAR_patch_UNVERIFIED','QW_DTM_north_edge_ramp_UNVERIFIED','WU_richardson_reid_LiDAR_patch_UNVERIFIED','WF_east_dorm_LiDAR_terrain_patch_UNVERIFIED','WN_south_wood_LiDAR_patch_ext_UNVERIFIED','WO_gully_head_LiDAR_patch_UNVERIFIED']
dg=bpy.context.evaluated_depsgraph_get()
def mesh(o):
    e=o.evaluated_get(dg); m=e.to_mesh(); V=[o.matrix_world@v.co for v in m.vertices]; P=[tuple(p.vertices) for p in m.polygons]; N=[(o.matrix_world.to_3x3()@p.normal).normalized() for p in m.polygons]; e.to_mesh_clear(); return V,P,N
def hz(b,x,y):
    h=b.ray_cast(Vector((x,y,500)),Vector((0,0,-1))); return h[0].z if h[0] is not None else None
rep={}
for n in ROADS+WALKS+GRD:
    o=O.get(n); 
    if o: 
        V,P,N=mesh(o); zs=[v.z for v in V]
        rep['info_'+n]=dict(v=len(V),f=len(P),zmin=round(min(zs),3),zmax=round(max(zs),3),mods=[m.type+':'+m.name for m in o.modifiers],up=sum(1 for q in N if q.z>0.5),side=sum(1 for q in N if abs(q.z)<0.5),down=sum(1 for q in N if q.z<-0.5))
        print('INFO',n,rep['info_'+n],flush=True)
WB={n:BVHTree.FromPolygons(*mesh(O[n])[:2]) for n in WALKS if O.get(n)}
GB={n:BVHTree.FromPolygons(*mesh(O[n])[:2]) for n in GRD if O.get(n)}
def walk_at(x,y):
    return any(hz(b,x,y) is not None for b in WB.values())
def gz(x,y):
    r=[(hz(b,x,y),n) for n,b in GB.items()]; r=[t for t in r if t[0] is not None]; return max(r) if r else (None,None)
samples=[]
for rn in ROADS:
    o=O.get(rn)
    if not o: continue
    V,P,N=mesh(o); RB=BVHTree.FromPolygons(V,P)
    # top-face boundary edges
    from collections import Counter
    ec=Counter()
    for p,q in zip(P,N):
        if q.z<0.5: continue
        for i in range(len(p)): ec[tuple(sorted((p[i],p[(i+1)%len(p)])))]+=1
    bed=[e for e,c in ec.items() if c==1]
    for a,b in bed:
        A,B=V[a],V[b]; L=(B-A).length
        if L<1e-3: continue
        t=(B-A).normalized(); nrm=Vector((-t.y,t.x,0))
        for s in np.arange(0.0,L,0.5):
            p=A+(B-A)*(s/L)
            # outward = side where road top not present
            mid=Vector((p.x+nrm.x*0.3,p.y+nrm.y*0.3,0))
            if hz(RB,mid.x,mid.y) is not None: nrm=-nrm
            top=p.z; row={'road':rn[:2],'x':round(p.x,2),'y':round(p.y,2),'top':round(top,3)}
            for d in (0.1,0.25,0.5,1.0):
                q=(p.x+nrm.x*d,p.y+nrm.y*d)
                w=walk_at(*q); g,gn=gz(*q)
                row[f'g{d}']=None if g is None else round(g,3); row[f'w{d}']=w; row[f'n{d}']=gn and gn[:4]
            samples.append(row)
lawn=[r for r in samples if not r['w0.1'] and not r['w0.25'] and r['g0.25'] is not None]
ex=np.array([r['top']-r['g0.25'] for r in lawn]) if lawn else np.array([0])
rep['n_samples']=len(samples); rep['n_lawnside']=len(lawn)
rep['exposure_0.25']=dict(min=round(float(ex.min()),3),p50=round(float(np.median(ex)),3),p90=round(float(np.percentile(ex,90)),3),max=round(float(ex.max()),3),n_gt5cm=int((ex>0.05).sum()),n_gt10=int((ex>0.10).sum()),n_lt0=int((ex<0).sum()))
for rn in ('QS','QW'):
    e=np.array([r['top']-r['g0.25'] for r in lawn if r['road']==rn])
    if len(e): rep['exp_'+rn]=dict(n=len(e),p50=round(float(np.median(e)),3),p90=round(float(np.percentile(e,90)),3),max=round(float(e.max()),3),n_gt5=int((e>0.05).sum()))
print('REP',json.dumps({k:v for k,v in rep.items() if not k.startswith('info')}),flush=True)
json.dump(dict(rep=rep,samples=samples),open(f'{R}/data/ww/probe.json','w'),indent=0)
print('EXIT',flush=True)
