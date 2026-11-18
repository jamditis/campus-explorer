"""we probe: (a) walk 436 boundary exposure hot spots; (b) Stone junction wedge; (c) x54-60,y280-295 gap."""
import bpy,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from collections import Counter
O=bpy.data.objects; dg=bpy.context.evaluated_depsgraph_get()
def mesh(o):
    e=o.evaluated_get(dg); m=e.to_mesh(); V=[o.matrix_world@v.co for v in m.vertices]; P=[tuple(p.vertices) for p in m.polygons]; N=[(o.matrix_world.to_3x3()@p.normal).normalized() for p in m.polygons]; e.to_mesh_clear(); return V,P,N
def bvh(o): V,P,_=mesh(o); return BVHTree.FromPolygons(V,P)
def top(B,x,y):
    z=[(h[0].z,i) for i,b in enumerate(B) for h in [b.ray_cast(Vector((x,y,500)),Vector((0,0,-1)))] if h[0] is not None]; return max(z) if z else None
SLn=[n for n in O.keys() if O[n].type=='MESH' and n.startswith(('QS_footway_','QW_footway_','QS_service_','TR_footway','SG_'))]
GRDn=[n for n in O.keys() if O[n].type=='MESH' and n.startswith(('WV_stone','WN_south','WO_gully','Terrain_LiDAR','QW_DTM','WU_rich','WT_rich','WF_east','RZ2_','WA0_','SA_ground_lower_patch'))]
SL=[bvh(O[n]) for n in SLn]; G=[bvh(O[n]) for n in GRDn]
SK=bvh(O['Context_skirt_3DEP_ortho_4km'])
V,P,N=mesh(O['QS_footway_313027436_UNVERIFIED']); ec=Counter()
for p,q in zip(P,N):
    if q.z<0.5: continue
    for i in range(len(p)): ec[tuple(sorted((p[i],p[(i+1)%len(p)])))]+=1
bp=[]
for (a,b),c in ec.items():
    if c!=1: continue
    A,B=V[a],V[b]; n=max(1,int((B-A).length/0.2))
    for k in range(n+1): bp.append(A+(B-A)*(k/n))
xs=[p.x for p in bp]; ys=[p.y for p in bp]; print('436 bbox',min(xs),max(xs),min(ys),max(ys),len(bp),flush=True)
hot=[]
for p in bp:
    for ang in np.linspace(0,2*np.pi,16,endpoint=False):
        x=p.x+0.3*np.cos(ang); y=p.y+0.3*np.sin(ang)
        if top(SL,x,y) is not None: continue
        g=top(G,x,y)
        if g is None: hot.append((round(p.x,1),round(p.y,1),'NOGROUND')); break
        e=p.z-g[0]
        if e>0.04: hot.append((round(p.x,1),round(p.y,1),round(e,3),GRDn[g[1]][:3]))
        break
print('HOT436',len(hot),hot[:60],flush=True)
# wedge
for x in np.arange(143.0,144.8,0.2):
    row=[]
    for y in np.arange(293.6,296.6,0.4):
        s=top(SL,x,y); g=top(G,x,y)
        row.append(('S%.2f'%s[0] if s else '-')+'/'+('G%.2f'%g[0]+GRDn[g[1]][:2] if g else 'g-'))
    print('WEDGE x%.1f'%x,row,flush=True)
# gap
nog=0; tot=0; pts=[]
for x in np.arange(54,60.01,0.5):
    for y in np.arange(280,295.01,0.5):
        tot+=1
        if top(SL,x,y) is None and top(G,x,y) is None:
            nog+=1; h=SK.ray_cast(Vector((x,y,500)),Vector((0,0,-1))); pts.append((x,y,round(h[0].z,2) if h[0] else None))
print('GAP',nog,tot,pts[:40],flush=True)
# what's there per object (any mesh) at a few gap points
for (x,y,_) in pts[:6]:
    h=bpy.context.scene.ray_cast(dg,Vector((x,y,160)),Vector((0,0,-1)))
    print('GAPHIT',x,y,h[0] and (round(h[1].z,2),h[4].name),flush=True)
