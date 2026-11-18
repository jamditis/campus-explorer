"""wt fix3 (review): (a) profile probe along the eye-from-E view for the dark lawn line; (b) tuck the WT patch 3 cm under
walk / soil-edge / apron slabs (only where lowering <= 0.15 m: a genuine poke, never pulling ground down to a low old slab) where the 1 m patch poked through their large triangles (dark slivers on walk 313027429 in close-up)."""
import bpy, json, math, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R='/workspace/nj-scenes/montclair-state'
import os
PROBE=not os.environ.get('NOPROBE')
CAP=float(os.environ.get('TUCKCAP','0.15'))
O=bpy.data.objects; sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
def bvh(o):
    e=o.evaluated_get(dg); m=e.to_mesh(); b=BVHTree.FromPolygons([o.matrix_world@v.co for v in m.vertices],[tuple(p.vertices) for p in m.polygons]); e.to_mesh_clear(); return b
GN=['Context_skirt_3DEP_ortho_4km','WT_richardson_west_LiDAR_patch_UNVERIFIED','RZ2_SC_LiDAR_ground_patch_UNVERIFIED','QW_DTM_north_edge_ramp_UNVERIFIED','WF_east_dorm_LiDAR_terrain_patch_UNVERIFIED','Terrain_LiDAR_DTM_1m']
GB={n:bvh(O[n]) for n in GN}
def top(x,y):
    best=(None,None)
    for n,b in GB.items():
        h=b.ray_cast(Vector((x,y,500)),Vector((0,0,-1)))[0]
        if h is not None and (best[0] is None or h.z>best[0]): best=(h.z,n)
    return best
out=[]
for ang in ((-12,-6,0,6,12) if PROBE else ()):
    P=Vector((90,312)); T=Vector((50,300)); d=(T-P).normalized(); a=math.radians(ang); d=Vector((d.x*math.cos(a)-d.y*math.sin(a),d.x*math.sin(a)+d.y*math.cos(a)))
    prev=None
    for k in range(0,160):
        q=P+d*(k*0.25); z,n=top(q.x,q.y)
        if prev and z is not None and prev[0] is not None and (abs(z-prev[0])>0.04 or n!=prev[1]):
            out.append([ang,round(q.x,2),round(q.y,2),round(z-prev[0],3),prev[1][:6],n[:6]])
        prev=(z,n)
for o in out: print('JUMP',o)
# (b) walk tuck
E=O['WT_richardson_west_LiDAR_patch_UNVERIFIED']; me=E.data; mw=E.matrix_world; mi=mw.inverted()
if os.environ.get('RESTORE'):
    B=np.load(f'{R}/data/wt/wt_patch_pre_fix3.npy')
    for v,c in zip(me.vertices,B): v.co=c
    me.update(); print('RESTORED')
else: np.save(f'{R}/data/wt/wt_patch_pre_fix3.npy',np.array([v.co[:] for v in me.vertices]))
SL=[o for o in O if o.type=='MESH' and o.name.startswith(('QS_footway','QT_soil_edge','QW_footway','QW_soil_edge','QQ_Richardson_paved_apron'))]
SB=[bvh(o) for o in SL]
n=0;mx=0.0
for v in me.vertices:
    c=mw@v.co; lo=None
    for dx,dy in ((0,0),(0.5,0),(-0.5,0),(0,0.5),(0,-0.5)):
        for b in SB:
            h=b.ray_cast(Vector((c.x+dx,c.y+dy,500)),Vector((0,0,-1)))[0]
            if h is not None and (lo is None or h.z<lo): lo=h.z
    if lo is not None and c.z>lo-0.03 and c.z-(lo-0.03)<=CAP:
        d=c.z-(lo-0.03); c.z=lo-0.03; v.co=mi@c; n+=1; mx=max(mx,d)
me.update(); print('TUCK',n,round(mx,3))
r=json.load(open(f'{R}/data/wt/fix_report.json')); r['fix3_jumps']=out; r['fix3_walk_tuck']=[n,round(mx,3),'cap',CAP]; json.dump(r,open(f'{R}/data/wt/fix_report.json','w'),indent=1)
bpy.ops.wm.save_mainfile(); print('SAVED')
