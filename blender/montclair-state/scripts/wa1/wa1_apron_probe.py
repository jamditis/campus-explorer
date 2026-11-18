import bpy, numpy as np, json
from collections import defaultdict
from mathutils import Vector
from mathutils.bvhtree import BVHTree
O=bpy.data.objects; dg=bpy.context.evaluated_depsgraph_get()
def bvh(o):
    e=o.evaluated_get(dg); m=e.to_mesh(); b=BVHTree.FromPolygons([o.matrix_world@v.co for v in m.vertices],[tuple(p.vertices) for p in m.polygons]); e.to_mesh_clear(); return b
G=[bvh(O[n]) for n in O.keys() if O[n].type=='MESH' and n.startswith(('WV_stone','WN_south','WO_gully','Terrain_LiDAR','QW_DTM','WU_rich','WT_rich','WF_east','RZ2_','WA0_'))]
SK=bvh(O['Context_skirt_3DEP_ortho_4km'])
def gz(x,y):
    z=[h[0].z for b in G for h in [b.ray_cast(Vector((x,y,500)),Vector((0,0,-1)))] if h[0] is not None]
    return max(z) if z else None
a=O['QQ_Richardson_paved_apron_UNVERIFIED']; mw=a.matrix_world
ec=defaultdict(list)
for p in a.data.polygons:
    L=list(p.vertices)
    for u,v in zip(L,L[1:]+L[:1]): ec[(min(u,v),max(u,v))].append(p.index)
bd=[k for k,c in ec.items() if len(c)==1]
print('boundary edges',len(bd))
bad=[]; allr=[]
for u,v in bd:
    A=mw@a.data.vertices[u].co; B=mw@a.data.vertices[v].co
    for f in (0.25,0.75):
        P=A.lerp(B,f)
        # outward direction: average polygon normal in plane; use edge perp pointing away from face centre
        poly=a.data.polygons[ec[(u,v)][0]]; c=mw@poly.center
        e=(B-A); e.z=0; e.normalize(); n=Vector((-e.y,e.x,0))
        if n.dot(P-c)<0: n=-n
        for off in (0.0,0.15,0.3):
            Q=P+n*off; g=gz(Q.x,Q.y)
            gap=None if g is None else round((P.z-g)*100,1)
            allr.append((round(P.x,1),round(P.y,1),off,gap))
            if g is None or P.z-g>8:
                bad.append((round(P.x,1),round(P.y,1),off,gap))
print('samples',len(allr),'bad (no ground or apron >8cm above ground)',len(bad))
import collections
cl=collections.Counter((round(x/5)*5,round(y/5)*5) for x,y,o,g in bad)
print('bad clusters (5m cell: count)',sorted(cl.items()))
nog=[b for b in bad if b[3] is None]; print('no ground at all',len(nog), nog[:20])
big=sorted([b for b in bad if b[3] is not None],key=lambda b:-b[3])[:15]; print('worst',big)
json.dump(bad,open('data/wa1/apron_bad.json','w'))
sc=bpy.context.scene
exp=[]
seen=set()
for x,y,off,g in bad:
    if g is not None or off!=0.0: continue
    exp.append((x,y))
# re-derive with outward ray test
res=[]
for u,v in bd:
    A=mw@a.data.vertices[u].co; B=mw@a.data.vertices[v].co
    poly=a.data.polygons[ec[(u,v)][0]]; c=mw@poly.center
    e=(B-A); e.z=0; e.normalize(); n=Vector((-e.y,e.x,0))
    for f in (0.25,0.75):
        P=A.lerp(B,f)
        if n.dot(P-c)<0: nn=-n
        else: nn=n
        if gz(P.x+nn.x*0.3,P.y+nn.y*0.3) is not None and gz(P.x,P.y) is not None: continue
        if gz(P.x,P.y) is not None and gz(P.x+nn.x*.3,P.y+nn.y*.3) is None: kind='ground ends before 0.3'
        else: kind='no ground'
        o=P-Vector((0,0,0.05)); hit=sc.ray_cast(dg,o,nn,distance=0.5)
        wall=hit[0] and not hit[4].name.startswith(('Context_skirt','Terrain','WU_','WV_','WT_','WF_','QW_','RZ2'))
        hit2=sc.ray_cast(dg,P+nn*0.2+Vector((0,0,0.5)),Vector((0,0,-1)))
        under=hit2[4].name if hit2[0] else None
        res.append((round(P.x,1),round(P.y,1),kind,'wall:'+hit[4].name[:24] if wall else 'open',under))
op=[r for r in res if r[3]=='open']
print('EXPOSED (not against wall)',len(op),'of',len(res))
cl=collections.Counter((round(r[0]/5)*5,round(r[1]/5)*5,r[4]) for r in op); print('EXPCL',sorted(cl.items(),key=lambda kv:-kv[1])[:30])
json.dump(op,open('data/wa1/apron_exposed.json','w'))
