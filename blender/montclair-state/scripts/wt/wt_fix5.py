"""wt fix5 (review): snap the patch's open (skirt-facing) boundary verts to the final evaluated skirt z - 1 cm (skirt there is no longer
moved by the WT GN, fix4) and fade that offset inward over 3 m. Only |offset|<=0.20 m (bigger ones are not open-skirt lips; listed, untouched). Removes the residual 2-9 cm lip at x=80 seen in the E eye view."""
import bpy, json, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree
R='/workspace/nj-scenes/montclair-state'
O=bpy.data.objects; dg=bpy.context.evaluated_depsgraph_get()
def ss(t):
    t=min(max(t,0.0),1.0); return t*t*(3-2*t)
def bvh(o):
    e=o.evaluated_get(dg); m=e.to_mesh(); b=BVHTree.FromPolygons([o.matrix_world@v.co for v in m.vertices],[tuple(p.vertices) for p in m.polygons]); e.to_mesh_clear(); return b
E=O['WT_richardson_west_LiDAR_patch_UNVERIFIED']; me=E.data; mw=E.matrix_world; mi=mw.inverted()
B=np.load(f'{R}/data/wt/wt_patch_pre_fix5.npy')
for v,c in zip(me.vertices,B): v.co=c
me.update()
BS=bvh(O['Context_skirt_3DEP_ortho_4km']); BE=bvh(E)
NB=[bvh(O[n]) for n in ('RZ2_SC_LiDAR_ground_patch_UNVERIFIED','QW_DTM_north_edge_ramp_UNVERIFIED','WF_east_dorm_LiDAR_terrain_patch_UNVERIFIED','Terrain_LiDAR_DTM_1m','QT_Richardson_base_plinth_UNVERIFIED','QP_Richardson_ground_storey_glass_piers_UNVERIFIED','QP_Richardson_white_corner_towers_UNVERIFIED','QU_G_floor_UNVERIFIED','MO Health Drop-In Center walls+parapet+roof (best-effort; UNVER')]
def hit(b,x,y): return b.ray_cast(Vector((x,y,500)),Vector((0,0,-1)))[0]
cnt={}
for p in me.polygons:
    for ek in p.edge_keys: cnt[ek]=cnt.get(ek,0)+1
bv=set()
for ek,c in cnt.items():
    if c==1: bv.update(ek)
off={}; BIG=[]
for i in bv:
    c=mw@me.vertices[i].co
    for dx,dy in ((0.7,0),(-0.7,0),(0,0.7),(0,-0.7)):
        x,y=c.x+dx,c.y+dy
        if hit(BE,x,y) is None and not any(hit(b,x,y) is not None for b in NB):
            h=hit(BS,c.x,c.y)
            if h is not None:
                d0=(h.z-0.01)-c.z
                if abs(d0)<=0.20: off[i]=d0
                else: BIG.append([round(c.x,1),round(c.y,1),round(d0,2)])
            break
kt=KDTree(len(off))
for i in off: kt.insert(me.vertices[i].co,i)
kt.balance()
mx=0.0; n=0
for v in me.vertices:
    if v.index in off: d=off[v.index]
    else:
        res=kt.find_n(v.co,3); ws=0; s=0
        for _,j,dd in res:
            if dd<3.0: w=1-ss(dd/3.0); ws+=w; s+=w*off[j]
        d=s/ws*min(1,ws) if ws>0 else 0.0
    if abs(d)>1e-4:
        c=mw@v.co; c.z+=d; v.co=mi@c; n+=1; mx=max(mx,abs(d))
me.update()
vals=list(off.values()); print('BIG',BIG); print('SNAP open',len(off),'moved',n,'max',round(mx,3),'off med',round(float(np.median(vals)),3),'min',round(min(vals),3),'max',round(max(vals),3))
r=json.load(open(f'{R}/data/wt/fix_report.json')); r['fix5_open_snap']={'open':len(off),'moved':n,'max':round(mx,3),'off_min':round(min(vals),3),'off_max':round(max(vals),3),'skipped_gt_0.20m':BIG}; json.dump(r,open(f'{R}/data/wt/fix_report.json','w'),indent=1)
bpy.ops.wm.save_mainfile(); print('SAVED')
