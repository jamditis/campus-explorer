"""wd: narrow every QT walk soil-edge strip from ~22 cm to ~11 cm (outer verts pulled halfway toward the slab edge, then
re-seated on the ground +0.5 cm; inner verts untouched). The 22 cm pale strip read as a wide tan band in low eye views
(W eye at Richardson west). Ground = first non-slab/strip/vegetation hit from above."""
import bpy,numpy as np,json,sys
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R='/workspace/nj-scenes/montclair-state'; O=bpy.data.objects; sc=bpy.context.scene
FAC=0.5; OFF=0.005
dg=bpy.context.evaluated_depsgraph_get()
SKIP=('QS_','QT_','QW_footway','QS_service','TR_footway','SG_','cx_','RG_','tree','Tree','leaf','lamp','Lamp','bench','WC_','WA','WB')
GRD=[n for n in O.keys() if O[n].type=='MESH' and n.startswith(('WT_richardson_west_LiDAR','RZ2_','WF_east_dorm_LiDAR','WU_richardson_reid','QW_DTM'))]
def _bvh(o):
    e=o.evaluated_get(bpy.context.evaluated_depsgraph_get()); m=e.to_mesh(); V=[o.matrix_world@v.co for v in m.vertices]; P=[tuple(p.vertices) for p in m.polygons]; e.to_mesh_clear(); return BVHTree.FromPolygons(V,P)
GB=[]
def rebuild():
    GB.clear(); GB.extend(_bvh(O[n]) for n in GRD)
rebuild(); print('GRD',GRD,flush=True)
BX=(40,76,294,326); FADE=2.0
def ground(x,y):
    z=[h[0].z for b in GB for h in [b.ray_cast(Vector((x,y,500)),Vector((0,0,-1)))] if h[0] is not None]
    return (max(z),'') if z else None
def fac(x,y):
    dd=max(BX[0]-x,x-BX[1],BX[2]-y,y-BX[3],0.0)
    if dd>=FADE: return None
    w=dd/FADE; return FAC+(1-FAC)*w
rep={}; np_all=[]
names=[k for k in O.keys() if k.startswith('QT_soil_edge_') and any(t in k for t in ('313027435','313027436','313027429'))]
PRE={}
for n in names:
    t=O[n]; s=O[n.replace('QT_soil_edge_','QS_footway_')]
    sm=s.data; V=[s.matrix_world@v.co for v in sm.vertices]; B=BVHTree.FromPolygons(V,[tuple(p.vertices) for p in sm.polygons])
    mw=t.matrix_world; mi=mw.inverted(); PRE[n]=np.array([v.co[:] for v in t.data.vertices]); np.save(f'{R}/data/wd/{n}_pre.npy',PRE[n])
    moved=0; gnone=0; lift=[]
    for v in t.data.vertices:
        w=mw@v.co; loc,nrm,idx,d=B.find_nearest(w)
        if d<0.05: continue
        f=fac(w.x,w.y)
        if f is None: continue
        dx=Vector((w.x-loc.x,w.y-loc.y))
        nx=loc.x+dx.x*f; ny=loc.y+dx.y*f
        g=ground(nx,ny)
        if g is None: gnone+=1; continue
        nz=g[0]+OFF
        lift.append(nz-w.z)
        v.co=mi@Vector((nx,ny,nz)); moved+=1
    t.data.update()
    lift=np.array(lift) if lift else np.zeros(1)
    rep[n]=dict(moved=moved,gnone=gnone,dz_p10=round(float(np.percentile(lift,10)),3),dz_p50=round(float(np.median(lift)),3),dz_p90=round(float(np.percentile(lift,90)),3),dz_min=round(float(lift.min()),3),dz_max=round(float(lift.max()),3))
    print('STRIP',n,rep[n],flush=True)
bpy.context.view_layer.update()
# poke check: ground above strip at poly centres (strip must be on top)
pk=0; tot=0
for n in names:
    t=O[n]; mw=t.matrix_world
    for p in t.data.polygons:
        c=mw@p.center
        if fac(c.x,c.y) is None: continue
        g=ground(c.x,c.y)
        if g is None: continue
        tot+=1
        if g[0]>c.z+0.002: pk+=1
rep['pokes']=[pk,tot]; print('POKES',pk,tot,flush=True)
json.dump(rep,open(f'{R}/data/wd/narrow_report.json','w'),indent=1)
if '--save' in sys.argv: bpy.ops.wm.save_mainfile(); print('SAVED',len(O),flush=True)
