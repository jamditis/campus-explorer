# ws207 W12 "bite" at (9,-39) = where the OSM walk crosses the CCOM dock apron's SW corner the two sheets are nearly
# coplanar (walk 135.41 vs apron 135.42 @ (8.6,-38.5), crossing slopes), so the top surface flips along a jagged line and the
# walk's own wiggly E edge (map206: 0.3-0.9 m teeth at y -37..-38.6) cuts white teeth into the dark apron.
# Fix (z-order + straight edge): (1) walk E-edge boundary verts for y -38.5..-35.2 snapped onto the straight line
# P1(6.35,-35.5) -> P2(8.65,-38.5) (P2 = where the walk edge meets the apron S edge; south of P2 the ws206 straight edge
# continues); (2) walk verts over the apron raised to apron + 5 mm, 0.6 m smoothstep taper outside (raise-only), so the walk
# is one clean concrete band crossing the asphalt apron. A fillet slab (fix207c_fillet_REJECTED.py) was tried and rejected.
import bpy, bmesh, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
def ob(p): return [o for o in bpy.data.objects if o.name.startswith(p)][0]
def hz(t,x,y):
    h=t.ray_cast(Vector((x,y,160)),Vector((0,0,-1)),80); return h[0].z if h[0] is not None else None
FP=ob('Footpaths_OSM'); AP=ob('CCOM_dock_apron_20261014jf3')
am=AP.matrix_world; TA=BVHTree.FromPolygons([am@v.co for v in AP.data.vertices],[tuple(p.vertices) for p in AP.data.polygons])
P1=np.array([6.35,-35.5]); P2=np.array([8.65,-38.5])
def Lx(y): return P1[0]+(P2[0]-P1[0])*(y-P1[1])/(P2[1]-P1[1])
fm=FP.matrix_world; fi=fm.inverted()
bm=bmesh.new(); bm.from_mesh(FP.data); bm.verts.ensure_lookup_table()
ne=0; mxe=0
for v in bm.verts:
    if not v.is_boundary: continue
    g=fm@v.co
    if -38.5<=g.y<=-35.2 and g.x>Lx(g.y)-0.6 and g.x<Lx(g.y)+1.2:
        d=Lx(g.y)-g.x; mxe=max(mxe,abs(d)); g.x=Lx(g.y); v.co=fi@g; ne+=1
bm.to_mesh(FP.data); bm.free()
print('F207c walk E-edge verts snapped',ne,'max shift %.2f'%mxe,flush=True)
# subdivide the walk around the apron crossing so the raise follows the apron (walk faces here are ~1 m)
def inr(g): return 4.5<g.x<11.5 and -40.5<g.y<-35.5
for it in range(3):
    bm=bmesh.new(); bm.from_mesh(FP.data)
    E=[e for e in bm.edges if e.calc_length()>0.3 and all(inr(fm@v.co) for v in e.verts)]
    if not E: bm.free(); break
    bmesh.ops.subdivide_edges(bm,edges=E,cuts=1,use_grid_fill=True)
    bmesh.ops.triangulate(bm,faces=[f for f in bm.faces if len(f.verts)>4])
    bm.to_mesh(FP.data); bm.free(); print('F207c subdiv',len(E),flush=True)
# raise over apron
idx=[i for i,v in enumerate(FP.data.vertices) if 2<(fm@v.co).x<13 and -41<(fm@v.co).y<-33]
L=[]
for i in idx:
    g=fm@FP.data.vertices[i].co; za=hz(TA,g.x,g.y)
    if za is not None and g.z<za+0.005: L.append((g.x,g.y,za+0.005-g.z))
L=np.array(L) if L else np.zeros((0,3)); n=0; mx=0
for i in idx:
    v=FP.data.vertices[i]; g=fm@v.co
    if not len(L): break
    d=np.sqrt((L[:,0]-g.x)**2+(L[:,1]-g.y)**2); f=np.clip(1-d/0.6,0,1); f=f*f*(3-2*f); up=float((L[:,2]*f).max())
    if up>1e-5: g.z+=up; v.co=fi@g; n+=1; mx=max(mx,up)
FP.data.update(); print('F207c walk verts raised over apron',n,'max %.3f'%mx,flush=True)
