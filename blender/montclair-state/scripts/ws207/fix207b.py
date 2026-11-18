# ws207 W12 leftover: CCOM dock apron (CCOM_dock_apron_20261014jf3) E edge "zigzag" + walk/apron bite at (9,-39).
# outl: the apron outline is a clean rotated rectangle (E edge (15.25,-24.67)->(11.58,-39.21), S edge -> (-2.48,-35.67)),
# so the zigzag is the 1 m LiDAR Terrain poking through the apron's sloped edge (lawn triangles cut it). Same rule as
# fix206c (ws206 walk): a paved apron is flush with the lawn -> lower-only Terrain edit: verts under the apron -> apron-3 cm,
# within 1.0 m outside -> 1 cm under the nearest apron height, 1.0-1.3 m feather (0.2 m/m), never more than 0.5 m. Nothing raised.
import bpy, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
def ob(p): return [o for o in bpy.data.objects if o.name.startswith(p)][0]
def hz(t,x,y):
    h=t.ray_cast(Vector((x,y,160)),Vector((0,0,-1)),80); return h[0].z if h[0] is not None else None
AP=ob('CCOM_dock_apron_20261014jf3'); TER=ob('Terrain_LiDAR_DTM_1m')
am=AP.matrix_world; TA=BVHTree.FromPolygons([am@v.co for v in AP.data.vertices],[tuple(p.vertices) for p in AP.data.polygons])
FP=ob('Footpaths_OSM'); fm=FP.matrix_world; idx=[i for i,v in enumerate(FP.data.vertices) if 0<(fm@v.co).x<20 and -64<(fm@v.co).y<-28]
vs=set(idx); TF=BVHTree.FromPolygons([fm@v.co for v in FP.data.vertices],[tuple(p.vertices) for p in FP.data.polygons if all(i in vs for i in p.vertices)])
tm=TER.matrix_world; ti=tm.inverted(); n1=n2=0; mx=0
ang=np.linspace(0,2*np.pi,17)[:-1]
def pz(x,y):
    z=[q for q in (hz(TA,x,y),hz(TF,x,y)) if q is not None]; return min(z) if z else None
for v in TER.data.vertices:
    g=tm@v.co
    if not (6<g.x<17.5 and -41.5<g.y<-22): continue
    za=pz(g.x,g.y); cap=None
    if za is not None: cap=za-0.03
    else:
        for r in (0.2,0.4,0.6,0.8,1.0,1.15,1.3):
            zs=[pz(g.x+r*np.cos(a),g.y+r*np.sin(a)) for a in ang]; zs=[z for z in zs if z is not None]
            if zs: cap=min(zs)-0.01+(0.2*(r-1.0) if r>1.0 else 0); break
    if cap is not None and g.z>cap:
        cap=max(cap,g.z-0.5); mx=max(mx,g.z-cap); g.z=cap; v.co=ti@g
        if za is not None: n1+=1
        else: n2+=1
TER.data.update(); print('F207b terrain lowered under apron/walk',n1,'edge band',n2,'max %.3f'%mx,flush=True)
