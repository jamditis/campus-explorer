"""wx fix (B): Stone Hall west wall-foot humps. WV/QW-ramp ground verts INSIDE the Stone lower footprint (hidden by the
building) that sit above the outside grade make the faces crossing the wall rise as grey humps / poke through the
footway. Lower-only: inside verts within 3 m of the wall -> min(z, min of 4 nearest outside reference tops - 5 cm); verts
under a slab within 2 m of the wall -> min(z, slab - 3 cm). Walls, slabs, outside bare lawn untouched."""
import bpy, json, numpy as np, sys
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree
R='/workspace/nj-scenes/montclair-state'; O=bpy.data.objects
G=['WV_stone_west_LiDAR_patch_UNVERIFIED','QW_DTM_north_edge_ramp_UNVERIFIED']
GALL=G+['WF_east_dorm_LiDAR_terrain_patch_UNVERIFIED']
S=['QS_footway_546643369_UNVERIFIED','QT_soil_edge_546643369_UNVERIFIED','QS_service_546643370_UNVERIFIED','QW_footway_546643369_ext_UNVERIFIED','QW_soil_edge_546643369_ext_UNVERIFIED','QW_service_546643370_ext_UNVERIFIED','SG_QuadRoad_full_313028548_549_UNVERIFIED','TR_footway_546643369_S_gap_UNVERIFIED']
H=['TI_Stone_Hall_313028565_lower_UNVERIFIED','TQ_Stone_fascia_lower_UNVERIFIED']
BX=(120,155,248,322)
def bv(n):
    o=O[n]; m=o.data; return BVHTree.FromPolygons([o.matrix_world@v.co for v in m.vertices],[tuple(p.vertices) for p in m.polygons])
SB={n:bv(n) for n in S}; HB={n:bv(n) for n in H}
def top(B,x,y):
    z=None
    for b in B.values():
        r=b.ray_cast(Vector((x,y,400)),Vector((0,0,-1)))
        if r[0] is not None and (z is None or r[0].z>z): z=r[0].z
    return z
def inside(x,y): return top(HB,x,y) is not None
def pokes(GB):
    c=0;mx=0
    for x in np.arange(126,150,0.1):
      for y in np.arange(250,322,0.1):
        if inside(x,y): continue
        s=top(SB,x,y)
        if s is None: continue
        g=top(GB,x,y)
        if g is not None and g>s-0.005: c+=1; mx=max(mx,g-s)
    return c,round(mx,3)
GB0={n:bv(n) for n in GALL}
rep={'poke_before':pokes(GB0)}; print('POKE before',rep['poke_before'],flush=True)
ref=[]
for x in np.arange(BX[0],BX[1],0.25):
  for y in np.arange(BX[2],BX[3],0.25):
    if inside(x,y): continue
    s=top(SB,x,y); z=s if s is not None else top(GB0,x,y)
    if z is not None: ref.append((x,y,z))
kd=KDTree(len(ref))
for i,(x,y,z) in enumerate(ref): kd.insert(Vector((x,y,0)),i)
kd.balance()
for n in G:
    o=O[n]; me=o.data; mw=o.matrix_world; mi=mw.inverted()
    np.save(f'{R}/data/wx/{n[:12]}_pre_wx.npy',np.array([v.co[:] for v in me.vertices]))
    a=b=0; ma=mb=0.0
    for v in me.vertices:
        c=mw@v.co
        if not (BX[0]<=c.x<=BX[1] and BX[2]<=c.y<=BX[3]): continue
        if inside(c.x,c.y):
            co,i,d=kd.find(Vector((c.x,c.y,0)))
            if d>3.0: continue
            zz=min(ref[j][2] for _,j,_ in kd.find_n(Vector((c.x,c.y,0)),4))-0.05
            if c.z>zz: ma=max(ma,c.z-zz); c.z=zz; v.co=mi@c; a+=1
        else:
            s=top(SB,c.x,c.y)
            if s is None: continue
            near=any(inside(c.x+r*np.cos(t),c.y+r*np.sin(t)) for r in (0.5,1.0,2.0) for t in np.linspace(0,2*np.pi,8,endpoint=False))
            if near and c.z>s-0.03: mb=max(mb,c.z-(s-0.03)); c.z=s-0.03; v.co=mi@c; b+=1
    me.update(); rep[n[:12]]=dict(inside_lowered=a,max_in=round(ma,3),under_slab_lowered=b,max_us=round(mb,3)); print('FIX',n[:12],rep[n[:12]],flush=True)
GB1={n:bv(n) for n in GALL}
rep['poke_after']=pokes(GB1); print('POKE after',rep['poke_after'],flush=True)
for name in ('QS_Richardson_lawn_grass_points_UNVERIFIED','QV_Richardson_NW_lawn_grass_points_UNVERIFIED'):
    o=O.get(name); me=o.data; mw=o.matrix_world; mi=mw.inverted(); k=0
    for v in me.vertices:
        c=mw@v.co
        if not (126<=c.x<=150 and 250<=c.y<=322): continue
        g=top(GB1,c.x,c.y)
        if g is None: continue
        if inside(c.x,c.y):
            if c.z>g+0.01: c.z=g; v.co=mi@c; k+=1
            continue
        if abs(c.z-g)>0.01 and top(SB,c.x,c.y) is None: c.z=g; v.co=mi@c; k+=1
    me.update(); rep['grass_'+name[:2]]=k; print('GRASS',name[:2],k,flush=True)
json.dump(rep,open(f'{R}/data/wx/fix_report.json','w'),indent=1)
if '--save' in sys.argv: bpy.ops.wm.save_mainfile(); print('SAVED',len(O),flush=True)
