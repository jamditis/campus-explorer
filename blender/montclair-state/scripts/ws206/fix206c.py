# ws206 W12 (CCOM apron walk, OSM footpath x 4..12, y -36..-58 S of the CCOM dock apron): the walk's E edge read as a
# stair-stepped sawtooth. Cause (edge206.py): the walk outline itself is straight (E edge x 8.45@y-38 -> 11.6@y-45, then
# ~11.5 -> 10.0 to y-58) but the 1 m LiDAR Terrain pokes up to 0.38 m ABOVE the walk along that edge (y -36..-44, -46, -49.5),
# so the lawn's 1 m triangles cut bites out of the concrete. Real walks are flush with the lawn: lower-only Terrain edit in
# x 3..16, y -60..-33: verts under the walk -> walk - 3 cm (hidden), verts within 1.0 m of the walk -> capped 1 cm under the
# nearest walk height (lawn graded to the walk edge), 1.0-1.3 m -> cap rises 0.2 m/m (feather). Nothing raised.
import bpy, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
def ob(p): return [o for o in bpy.data.objects if o.name.startswith(p)][0]
def bvh(o):
    mw=o.matrix_world; return BVHTree.FromPolygons([mw@v.co for v in o.data.vertices],[tuple(p.vertices) for p in o.data.polygons])
def hz(t,x,y):
    h=t.ray_cast(Vector((x,y,160)),Vector((0,0,-1)),80); return h[0].z if h[0] is not None else None
FP=ob('Footpaths_OSM'); TER=ob('Terrain_LiDAR_DTM_1m')
fm=FP.matrix_world; idx=[i for i,v in enumerate(FP.data.vertices) if 0<(fm@v.co).x<20 and -64<(fm@v.co).y<-28]
vs=set(idx); polys=[tuple(p.vertices) for p in FP.data.polygons if all(i in vs for i in p.vertices)]
TF=BVHTree.FromPolygons([fm@v.co for v in FP.data.vertices],polys)
tm=TER.matrix_world; ti=tm.inverted(); n1=n2=0; mx=0
ang=np.linspace(0,2*np.pi,17)[:-1]
for v in TER.data.vertices:
    g=tm@v.co
    if not (3<g.x<16 and -60<g.y<-33): continue
    zf=hz(TF,g.x,g.y); cap=None
    if zf is not None: cap=zf-0.03
    else:
        for r in (0.2,0.4,0.6,0.8,1.0,1.15,1.3):
            zs=[hz(TF,g.x+r*np.cos(a),g.y+r*np.sin(a)) for a in ang]; zs=[z for z in zs if z is not None]
            if zs:
                cap=min(zs)-0.01+(0.2*(r-1.0) if r>1.0 else 0); break
    if cap is not None and g.z>cap:
        cap=max(cap,g.z-0.5)  # v2: never cut more than 0.5 m (LiDAR bump at (11.5,-42.5) was 1.1 m)
        mx=max(mx,g.z-cap); g.z=cap; v.co=ti@g
        if zf is not None: n1+=1
        else: n2+=1
TER.data.update(); print('F206c terrain lowered under walk',n1,'edge band',n2,'max %.3f'%mx,flush=True)
