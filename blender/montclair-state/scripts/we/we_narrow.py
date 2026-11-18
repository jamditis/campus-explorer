"""we (v2, outer-row only): narrow the remaining 5 QT walk soil-edge strips (428/430/432/437/546643369) from ~22 cm to ~11 cm, same method as
wd_narrow.py (outer/mid verts pulled halfway toward the slab edge, re-seated on LiDAR ground +0.5 cm; inner verts untouched).
Ground = per-object BVHs of the LiDAR/DTM patches only (no scene.ray_cast). If no ground hit, z is interpolated along the
existing strip surface. Whole strips (no box); pre-move coords saved to data/we/<name>_pre.npy."""
import bpy,numpy as np,json,sys
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R='/workspace/nj-scenes/montclair-state'; O=bpy.data.objects
import os
FAC=0.5; OUTW=0.11; OFF=0.005; CLAMP=float(os.environ.get('CLAMP','0.04'))  # QW ext strips: CLAMP=0 -> xy pull only, z kept (their ground sheet is not in GRD)
GRD=[n for n in O.keys() if O[n].type=='MESH' and n.startswith(('WV_stone','WN_south','WO_gully','Terrain_LiDAR','QW_DTM','WU_rich','WT_rich','WF_east','RZ2_','WA0_','SA_ground_lower_patch'))]
dg=bpy.context.evaluated_depsgraph_get()
def _bvh(o):
    e=o.evaluated_get(dg); m=e.to_mesh(); V=[o.matrix_world@v.co for v in m.vertices]; P=[tuple(p.vertices) for p in m.polygons]; e.to_mesh_clear(); return BVHTree.FromPolygons(V,P)
GB=[_bvh(O[n]) for n in GRD]; print('GRD',GRD,flush=True)
def ground(x,y,zref):
    # only hits within +-0.6 m of the strip (avoid odd far-above/below patches)
    z=[h[0].z for b in GB for h in [b.ray_cast(Vector((x,y,zref+0.6)),Vector((0,0,-1)),1.2)] if h[0] is not None]
    return max(z) if z else None
IDS=('313027428','313027430','313027432','313027437','546643369')
import os
QW=os.environ.get('QW')=='1'
names=[k for k in O.keys() if k.startswith('QW_soil_edge_')] if QW else [k for k in O.keys() if k.startswith('QT_soil_edge_') and any(t in k for t in IDS)]
print('NAMES',names,flush=True)
rep={}
for n in names:
    t=O[n]; s=O[n.replace('QW_soil_edge_','QW_footway_')] if QW else O[n.replace('QT_soil_edge_','QS_footway_')]
    sm=s.data; V=[s.matrix_world@v.co for v in sm.vertices]; B=BVHTree.FromPolygons(V,[tuple(p.vertices) for p in sm.polygons])
    mw=t.matrix_world; mi=mw.inverted(); pre=np.array([v.co[:] for v in t.data.vertices]); np.save(f'{R}/data/we/{n}_pre.npy',pre)
    moved=0; gnone=0; lift=[]; clamped=[]
    for v in t.data.vertices:
        w=mw@v.co; loc,nrm,idx,d=B.find_nearest(w)
        if d<0.05: continue   # inner row (on the slab side, ~5 cm under slab top) untouched; these 5 strips have only inner+outer rows (outer at ~0.20 m)
        f=OUTW/d
        nx=loc.x+(w.x-loc.x)*f; ny=loc.y+(w.y-loc.y)*f
        g=ground(nx,ny,w.z)
        zi=w.z
        if g is None: gnone+=1; nz=zi
        elif abs(g+OFF-w.z)>CLAMP: clamped.append((round(nx,2),round(ny,2),round(g+OFF-w.z,3))); nz=zi
        else: nz=g+OFF
        lift.append(nz-w.z); v.co=mi@Vector((nx,ny,nz)); moved+=1
    t.data.update()
    L=np.array(lift) if lift else np.zeros(1)
    rep[n]=dict(verts=len(t.data.vertices),moved=moved,gnone=gnone,dz_p10=round(float(np.percentile(L,10)),3),dz_p50=round(float(np.median(L)),3),dz_p90=round(float(np.percentile(L,90)),3),dz_min=round(float(L.min()),3),dz_max=round(float(L.max()),3),clamped=len(clamped),clamped_pts=clamped[:12])
    print('STRIP',n,rep[n],flush=True)
bpy.context.view_layer.update()
pk=0; tot=0; under=0
for n in names:
    t=O[n]; mw=t.matrix_world
    for p in t.data.polygons:
        c=mw@p.center; g=ground(c.x,c.y,c.z)
        if g is None: continue
        tot+=1
        if g>c.z+0.002: under+=1
        if g>c.z+0.03: pk+=1
rep['under_2mm']=[under,tot]; rep['under_3cm']=[pk,tot]; print('UNDER',under,pk,tot,flush=True)
json.dump(rep,open(f'{R}/data/we/narrow_report'+('_qw' if QW else '')+'.json','w'),indent=1)
if '--save' in sys.argv: bpy.ops.wm.save_mainfile(); print('SAVED',len(O),flush=True)
