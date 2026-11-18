# ws208 W12b: CCOM dock apron / walk junction flush. Cut render (ws208 0939 close-up) showed jagged light shards and a dark
# wedge where Footpaths_OSM (GN re-draped, evaluated z) crosses the CCOM_dock_apron: evaluated walk sits +30..45 mm over the
# apron across most of the crossing (lip with a ragged outline) but 5..57 mm UNDER it along its E edge (x 7..7.5,
# y -35..-37.5) and up to 25 mm under the WS206 E-edge fill just S of the apron -> apron/fill poke through the walk.
# Real site: concrete walk running flush off a concrete dock apron. Fix (non-GN objects only; walk untouched): apron/fill TOP
# verts under the evaluated walk -> walk z - 3 mm; verts within 1.2 m outside the walk feathered (IDW of edge deltas x smoothstep);
# long top edges in the zone split first so the feather is smooth. Zone x -0.5..12.5, y -41..-28.5 (keeps clear of the
# equipment platform/steps at y > -27). Evaluated walk tris from evdump208 (walk_eval_ws207a_apron.npz).
import bpy, bmesh, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree
D=np.load('/workspace/nj-scenes/montclair-state/scripts/ws208/walk_eval_ws207a_apron.npz')
W=BVHTree.FromPolygons([Vector(v) for v in D['V']],[tuple(map(int,f)) for f in D['F']])
X0,X1,Y0,Y1,FE=-0.5,12.5,-41.0,-28.5,1.2
def wz(x,y):
    h=W.ray_cast(Vector((x,y,140)),Vector((0,0,-1)),20); return h[0].z if h[0] is not None else None
for name in ('CCOM_dock_apron_20261014jf3','WS206_CCOM_walk_E_edge_straight_fill_ortho_LiDAR_UNVERIFIED'):
    o=bpy.data.objects[name]; mw=o.matrix_world; mi=mw.inverted()
    bm=bmesh.new(); bm.from_mesh(o.data); bm.normal_update()
    def inz(v):
        p=mw@v.co; return X0-FE<=p.x<=X1+FE and Y0-FE<=p.y<=Y1+FE
    def ezone(e):
        a=mw@e.verts[0].co; b=mw@e.verts[1].co
        for t in (0,0.25,0.5,0.75,1):
            p=a.lerp(b,t)
            if X0-FE<=p.x<=X1+FE and Y0-FE<=p.y<=Y1+FE: return True
        return False
    for _ in range(7):
        ed=[e for e in bm.edges if e.calc_length()>0.3 and ezone(e) and any(abs(f.normal.z)>0.7 for f in e.link_faces)]
        if not ed: break
        bmesh.ops.subdivide_edges(bm,edges=ed,cuts=1,use_grid_fill=True)
        bmesh.ops.triangulate(bm,faces=[f for f in bm.faces if len(f.verts)>4])
    bm.normal_update()
    top=[v for v in bm.verts if inz(v) and any(abs(f.normal.z)>0.7 for f in v.link_faces)]
    ins={};out=[]
    for v in top:
        p=mw@v.co
        if not (X0<=p.x<=X1 and Y0<=p.y<=Y1): out.append(v); continue
        z=wz(p.x,p.y)
        if z is not None: ins[v]=z-0.003-p.z
        else: out.append(v)
    kd=KDTree(len(ins)); L=list(ins.items())
    for i,(v,dl) in enumerate(L): kd.insert((mw@v.co).to_2d().to_3d(),i)
    kd.balance(); mv=0; mx=0
    for v,dl in L:
        dl=max(-0.08,min(0.08,dl)); p=mw@v.co; p.z+=dl; v.co=mi@p; mv+=1; mx=max(mx,abs(dl))
    for v in out:
        p=mw@v.co; q=p.to_2d().to_3d(); nb=kd.find_range(q,FE)
        if not nb: continue
        d0=min(d for _,_,d in nb); s=max(0,1-d0/FE); s=s*s*(3-2*s)
        w=[1/(d+0.05)**2 for _,_,d in nb]; dl=sum(wi*max(-0.08,min(0.08,L[i][1])) for wi,(_,i,_) in zip(w,nb))/sum(w)
        p.z+=dl*s; v.co=mi@p; mv+=1; mx=max(mx,abs(dl*s))
    bm.to_mesh(o.data); o.data.update(); bm.free()
    print('F208a',name[:30],'under-walk',len(ins),'moved',mv,'max %.3f'%mx,flush=True)
# NOTE: CCOM_dock_apron is a 30x30 single-sided 0.5 m grid with DOWNWARD normals -> top test uses |normal.z|.
