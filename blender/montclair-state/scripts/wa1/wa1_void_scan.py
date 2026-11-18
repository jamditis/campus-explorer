"""wa0 fix: (1) fill the WU building-mask void outside Richardson's walls (east tower corner slot) with a 0.1 m
2017-DTM-interpolated fill sheet 4 mm under WU; (2) tuck the QW ramp's floating x>=120 north strip under WV/WU
(dark crack lines in the E eye view); (3) seed QS grass points on the new bare fill. SAVE=1 to save."""
import bpy, bmesh, os, json, math, random
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree
R='/workspace/nj-scenes/montclair-state'; os.chdir(R)
O=bpy.data.objects; dg=bpy.context.evaluated_depsgraph_get(); rep={}
def bvh(names):
    V=[];P=[]
    for n in names:
        o=O[n]; e=o.evaluated_get(dg); m=e.to_mesh(); off=len(V)
        V+= [o.matrix_world@v.co for v in m.vertices]; P+=[tuple(off+i for i in p.vertices) for p in m.polygons]; e.to_mesh_clear()
    return BVHTree.FromPolygons(V,P)
WUN='WU_richardson_reid_LiDAR_patch_UNVERIFIED'; WVN='WV_stone_west_LiDAR_patch_UNVERIFIED'; QWN='QW_DTM_north_edge_ramp_UNVERIFIED'
WU=O[WUN]; B_WU=bvh([n for n in O.keys() if O[n].type=='MESH' and n.startswith(('WU_rich','WT_rich','WF_east','RZ2_','WA0_','Terrain_LiDAR','WV_stone','WN_south','WO_gully','QW_DTM'))]); B_WV=bvh([WVN]); B_QQ=bvh(['QQ_Richardson_paved_apron_UNVERIFIED'])
B_IN=bvh(['QU_G_floor_UNVERIFIED','QU_R_floor_UNVERIFIED','QP_Richardson_white_corner_towers_UNVERIFIED','QR_Richardson_tower_coping_lips_UNVERIFIED'])
B_TW=bvh(['QP_Richardson_white_corner_towers_UNVERIFIED','QR_Richardson_tower_coping_lips_UNVERIFIED'])
DN=Vector((0,0,-1)); UP=Vector((0,0,1))
def hz(b,x,y):
    h=b.ray_cast(Vector((x,y,400)),DN); return None if h[0] is None else h[0].z
def inside(b,x,y): return b.ray_cast(Vector((x,y,130.0)),UP)[0] is not None

wv=[o.matrix_world@v.co for o in [O[n] for n in O.keys() if O[n].type=='MESH' and n.startswith(('WU_rich','WT_rich','WF_east','RZ2_','WA0_'))] for v in o.data.vertices]; kd=KDTree(len(wv))
for i,c in enumerate(wv): kd.insert(c.to_2d().to_3d(),i)
kd.balance()
def idw(x,y):
    L=kd.find_range(Vector((x,y,0)),2.0)
    if len(L)<3: L=kd.find_n(Vector((x,y,0)),6)
    w=[1/max(d,0.05)**2 for _,_,d in L]; return sum(wi*wv[i].z for wi,(_,i,_) in zip(w,L))/sum(w)
S=0.1; X0,X1,Y0,Y1=55.0,120.0,245.0,325.0
nx=int(round((X1-X0)/S)); ny=int(round((Y1-Y0)/S))
cover=[]
for o in O:
    if o.type!='MESH' or o.name.startswith(('WU_rich','WT_rich','WF_east','RZ2_','WA0_','Terrain_LiDAR','WV_stone','WN_south','WO_gully','QW_DTM')) or o.name in (WUN,'QQ_Richardson_paved_apron_UNVERIFIED') or 'grass_points' in o.name or o.name.startswith(('Context_skirt','cx_grass','QP_Richardson','QT_Richardson','QU_','QR_Richardson')): continue
    if len(o.data.polygons)==0 and not o.modifiers: continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]; xs=[c.x for c in bb]; ys=[c.y for c in bb]; zs=[c.z for c in bb]
    if max(xs)<X0 or min(xs)>X1 or max(ys)<Y0 or min(ys)>Y1 or min(zs)>140: continue
    if (max(xs)-min(xs))>2000: continue
    cover.append(o.name)
print('cover objs',len(cover),flush=True); rep['cover_n']=len(cover)
B_CV=bvh(cover)
walls=[]
for o in O:
    if o.type!='MESH' or 'Richardson' not in o.name or not o.name.startswith('Q') or 'apron' in o.name: continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]; zs=[c.z for c in bb]
    if min(zs)<137.9<max(zs) and len(o.data.polygons)>0: walls.append(o.name)
print('walls',walls,flush=True); rep['walls']=walls
B_WL=bvh(walls)
def front_of_wall(x,y):
    if True: return False  # disabled: pier boxes give front faces from inside the glass storey (verified 276 faces up to 2.1 m inside the floor)
    best=None
    for k in range(16):
        a=k*math.pi/8; d=Vector((math.cos(a),math.sin(a),0))
        h=B_WL.ray_cast(Vector((x,y,137.9)),d,0.6)
        if h[0] is None: continue
        if best is None or h[3]<best[0]: best=(h[3],d.dot(h[1]))
    return best is not None and best[1]<0
void=set()
for j in range(ny):
    for i in range(nx):
        cx=X0+(i+.5)*S; cy=Y0+(j+.5)*S
        if hz(B_WU,cx,cy) is not None: continue
        if kd.find(Vector((cx,cy,0)))[2]>1.5: continue
        if B_CV.ray_cast(Vector((cx,cy,idw(cx,cy)+1.0)),DN,3.0)[0] is not None: continue
        corners=[(X0+(i+a)*S,Y0+(j+b)*S) for a in (0,1) for b in (0,1)]
        cin=inside(B_IN,cx,cy)
        if cin and not inside(B_TW,cx,cy):
            if not front_of_wall(cx,cy): continue
            rep.setdefault('wall_front_kept',0); rep['wall_front_kept']+=1
        elif cin:
            if all(inside(B_IN,*c) for c in corners): continue
        void.add((i,j))
print('void cells',len(void),flush=True)
def cz(i,j):
    cx=X0+(i+.5)*S; cy=Y0+(j+.5)*S; return cx,cy
keep=set(); skipped_apron=0
for (i,j) in void:
    cx,cy=cz(i,j); zf=idw(cx,cy)-0.004; za=hz(B_QQ,cx,cy)
    if za is not None and za>=zf-0.03: skipped_apron+=1; continue
    keep.add((i,j))

import collections
cl=collections.Counter((int((X0+(i+.5)*S)//2*2),int((Y0+(j+.5)*S)//2*2)) for i,j in void)
print('VOIDCL',sorted(cl.items()))
print('VOID_AREA_m2',len(void)*S*S)
