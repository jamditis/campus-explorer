"""wu fix3 (review): fade the north open edge y312-320 toward the evaluated skirt
where no WF/WT neighbour covers y=320 (the Reid-footprint hole in WF, x80-110).
Same idea as the east x112-120 fade — removes the ~0.46 m cliff in the N eye view.
Re-seat grass in the faded band by the same delta."""
import bpy, json, numpy as np, math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R='/workspace/nj-scenes/montclair-state'
O=bpy.data.objects
E=O['WU_richardson_reid_LiDAR_patch_UNVERIFIED']
sk=O['Context_skirt_3DEP_ortho_4km']
WF=O['WF_east_dorm_LiDAR_terrain_patch_UNVERIFIED']
WT=O['WT_richardson_west_LiDAR_patch_UNVERIFIED']
dg=bpy.context.evaluated_depsgraph_get()
def ss(t):
    t=min(max(t,0.0),1.0); return t*t*(3-2*t)
def bvh(o):
    e=o.evaluated_get(dg); m=e.to_mesh(); b=BVHTree.FromPolygons([o.matrix_world@v.co for v in m.vertices],[tuple(p.vertices) for p in m.polygons]); e.to_mesh_clear(); return b
def hz(b,x,y):
    h=b.ray_cast(Vector((x,y,500)),Vector((0,0,-1))); return h[0].z if h[0] is not None else None
BS=bvh(sk); BWF=bvh(WF); BWT=bvh(WT); BE=bvh(E)
me=E.data; mw=E.matrix_world; mi=mw.inverted()
np.save(f'{R}/data/wu/wu_patch_pre_fix3.npy',np.array([v.co[:] for v in me.vertices]))
n=0; mx=0.0; skipped_nb=0
oldz={}
for v in me.vertices:
    c=mw@v.co
    if c.y<312: continue
    if hz(BWF,c.x,320.4) is not None or hz(BWF,c.x,c.y+0.8) is not None:
        skipped_nb+=1; continue
    if hz(BWT,c.x,c.y) is not None and c.x<=80.05:
        skipped_nb+=1; continue
    s=hz(BS,c.x,320.6)
    if s is None: s=hz(BS,c.x,c.y)
    if s is None: continue
    w=ss((c.y-312.0)/8.0)
    if w<=1e-4: continue
    nz=c.z*(1-w)+s*w
    oldz[(round(c.x,3),round(c.y,3))]=c.z
    d=nz-c.z
    if abs(d)>1e-4:
        c.z=nz; v.co=mi@c; n+=1; mx=max(mx,abs(d))
me.update(); print('FADE north',n,'max',round(mx,3),'skipped_nb',skipped_nb,flush=True)
bpy.context.view_layer.update(); dg=bpy.context.evaluated_depsgraph_get(); BE2=bvh(E)
# grass: apply (new_patch - old_patch) inside y>=312 faces of the tile
gn=0; gmx=0.0
for name in ('QS_Richardson_lawn_grass_points_UNVERIFIED','QV_Richardson_NW_lawn_grass_points_UNVERIFIED'):
    o=O.get(name)
    if not o: continue
    meo=o.data; mwo=o.matrix_world; mio=mwo.inverted(); k=0; mm=0.0
    for v in meo.vertices:
        c=mwo@v.co
        if not (80<=c.x<=120 and 312<=c.y<=320): continue
        a0=hz(BE,c.x,c.y); a1=hz(BE2,c.x,c.y)
        if a0 is None or a1 is None: continue
        d=a1-a0
        if abs(d)<1e-4: continue
        c.z+=d; v.co=mio@c; k+=1; mm=max(mm,abs(d))
    meo.update(); print('GRASS fade',name[:2],k,round(mm,3),flush=True); gn+=k; gmx=max(gmx,mm)
r=json.load(open(f'{R}/data/wu/fix_report.json'))
r['fix3_north_fade']={'moved':n,'max':round(mx,3),'skipped_nb':skipped_nb,'grass':[gn,round(gmx,3)]}
json.dump(r,open(f'{R}/data/wu/fix_report.json','w'),indent=1)
bpy.ops.wm.save_mainfile(); print('SAVED',flush=True)
