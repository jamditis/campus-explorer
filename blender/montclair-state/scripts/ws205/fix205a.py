# ws205 W23 (Kasser-east lot entry aisle off College Ave bend): (1) the WS98 entry-aisle asphalt is a raw LiDAR drape with
# 1 m facets (local-plane residual rms 9.5 cm, max 39 cm) -> re-grade every vertex to a Gaussian (sigma 2 m) local-plane fit of the
# aisle itself (|dz|<=0.25 m; verts within 0.6 m of the College Ave carriageway/curb blended back to their old z so the flush joint
# stays closed). (2) the bare-ground triangle between the WS98 raised walk pad and the College Ave curb (x -207..-202, y -85..-92)
# is continuous light-grey paving in the NJ 2020 ortho (aisle -> OSM footpath crossing) -> one asphalt sheet (aisle material),
# graded by IDW from the surrounding paving edges (aisle S edge, footpath N edge, road edge, pad base = pad top - 0.15),
# tucked 4 mm under every existing surface so no existing edge moves. (3) Terrain verts fully under the aisle/fill lowered 3 cm
# under them (lower-only, hidden ground). Surface type of the triangle UNVERIFIED (asphalt vs concrete; ortho tone = aisle tone).
import bpy, bmesh, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
def ob(p): return [o for o in bpy.data.objects if o.name.startswith(p)][0]
def bvh(o):
    mw=o.matrix_world; me=o.data
    return BVHTree.FromPolygons([mw@v.co for v in me.vertices],[tuple(p.vertices) for p in me.polygons])
def hz(t,x,y):
    h=t.ray_cast(Vector((x,y,150)),Vector((0,0,-1)),60); return h[0].z if h[0] is not None else None
AI=ob('WS98_lotE_entry_aisle'); PAD=ob('WS98_lotE_raised_concrete_walk_pad'); RD=ob('WS27_CollegeAve_carriageway'); CR=ob('WS27_CollegeAve_curb_right')
FP=ob('Footpaths_OSM'); BED=ob('WS99_lotE_padS_bed'); TER=ob('Terrain_LiDAR_DTM_1m')
TRD=bvh(RD); TCR=bvh(CR)
# (1) aisle smoothing
mw=AI.matrix_world; mi=mw.inverted(); P=np.array([tuple(mw@v.co) for v in AI.data.vertices]); NZ=P[:,2].copy(); nb=0
def near_road(x,y):
    best=9
    for dx in np.arange(-0.6,0.61,0.2):
        for dy in np.arange(-0.6,0.61,0.2):
            if hz(TRD,x+dx,y+dy) is not None or hz(TCR,x+dx,y+dy) is not None: best=min(best,(dx*dx+dy*dy)**0.5)
    return best
for k,p in enumerate(P):
    d2=((P[:,:2]-p[:2])**2).sum(1); w=np.exp(-d2/8.0); X=np.c_[np.ones(len(P)),P[:,0]-p[0],P[:,1]-p[1]]; W=np.sqrt(w)
    z=np.linalg.lstsq(X*W[:,None],P[:,2]*W,rcond=None)[0][0]; dz=float(np.clip(z-p[2],-0.25,0.25))
    dr=near_road(p[0],p[1])
    if dr<0.6: dz*=dr/0.6; nb+=1
    NZ[k]=p[2]+dz
for k,v in enumerate(AI.data.vertices):
    g=mw@v.co; g.z=NZ[k]; v.co=mi@g
AI.data.update(); print('F205a aisle smoothed',len(P),'road-blended',nb,'max|dz| %.3f'%abs(NZ-P[:,2]).max(),flush=True)
# (2) triangle fill
TAI=bvh(AI); TPAD=bvh(PAD); TFP=bvh(FP); TBED=bvh(BED)
OTH=[TAI,TPAD,TRD,TCR,TFP,TBED]
SMP=[]
for x in np.arange(-208,-200.9,0.25):
    for y in np.arange(-97.5,-83.9,0.25):
        za=hz(TAI,x,y); zr=hz(TRD,x,y); zf=hz(TFP,x,y); zp=hz(TPAD,x,y)
        if za is not None and y<-83.0: SMP.append((x,y,za))
        elif zr is not None and x<-200.0: SMP.append((x,y,zr))
        elif zf is not None: SMP.append((x,y,zf))
        elif zp is not None and x>-207.6: SMP.append((x,y,zp-0.15))
SMP=np.array(SMP); print("F205a fit samples",len(SMP),flush=True)
def fz(x,y):
    d2=(SMP[:,0]-x)**2+(SMP[:,1]-y)**2; w=1/(d2+0.3)**2; return float((w*SMP[:,2]).sum()/w.sum())
POLY=[(-207.8,-84.3),(-201.2,-84.3),(-201.2,-96.5),(-207.8,-96.5)]
st=0.25; xs=np.arange(POLY[0][0],POLY[1][0]+1e-6,st); ys=np.arange(POLY[2][1],POLY[0][1]+1e-6,st)
bm=bmesh.new(); V={}
TT=bvh(TER)
for i,x in enumerate(xs):
    for j,y in enumerate(ys):
        z=fz(x,y)
        for t in OTH:
            zo=hz(t,x,y)
            if zo is not None and zo<z+0.004: z=zo-0.004
        V[(i,j)]=bm.verts.new((x,y,z))
nf=0
for i in range(len(xs)-1):
    for j in range(len(ys)-1):
        bm.faces.new([V[(i,j)],V[(i+1,j)],V[(i+1,j+1)],V[(i,j+1)]]); nf+=1
me=bpy.data.meshes.new('WS205_fill'); bm.to_mesh(me); bm.free()
for p in me.polygons: p.use_smooth=True
o=bpy.data.objects.new('WS205_lotE_entry_apron_asphalt_fill_ortho2020_UNVERIFIED',me); AI.users_collection[0].objects.link(o); me.materials.append(AI.data.materials[0])
print('F205a fill faces',nf,'z %.2f..%.2f'%(min(v.co.z for v in me.vertices),max(v.co.z for v in me.vertices)),flush=True)
# (3) lower covered Terrain verts (lower-only)
TF=bvh(o); tm=TER.matrix_world; ti=tm.inverted(); nl=0
for v in TER.data.vertices:
    g=tm@v.co
    if not (-218<g.x<-200 and -94<g.y<-67): continue
    zs=[]
    for dx,dy in ((0,0),(0.5,0),(-0.5,0),(0,0.5),(0,-0.5)):
        z=None
        for t in (TAI,TF):
            q=hz(t,g.x+dx,g.y+dy)
            if q is not None: z=q if z is None else min(z,q)
        if z is None: break
        zs.append(z)
    if len(zs)==5 and g.z>min(zs)-0.03:
        g.z=min(zs)-0.03; v.co=ti@g; nl+=1
TER.data.update(); print('F205a terrain lowered',nl,flush=True)
