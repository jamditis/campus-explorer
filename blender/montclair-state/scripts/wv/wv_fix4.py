"""wv fix4 (review): lawn showing through the Stone footway / Stone Street slabs between walk vertices
(N eye view: pale walk fragments). Measure patch-above-walk on a 0.25 m sample of every walk face in the
tile, then lower WV/WU-east/QW verts lying under a walk to walk-3 cm (no cap; covered by the slab) and
verts within 0.7 m of a walk by up to 0.30 m. Grass points under walks are dropped below the patch. Re-measure."""
import bpy, json, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R='/workspace/nj-scenes/montclair-state'
O=bpy.data.objects
WALKS=['QS_service_546643370_UNVERIFIED','QS_footway_546643369_UNVERIFIED','TR_footway_546643369_S_gap_UNVERIFIED','SG_QuadRoad_full_313028548_549_UNVERIFIED','QW_footway_546643369_ext_UNVERIFIED','QW_service_546643370_ext_UNVERIFIED']
GRD=['WV_stone_west_LiDAR_patch_UNVERIFIED','QW_DTM_north_edge_ramp_UNVERIFIED']
X0,X1,Y0,Y1=119.5,155.5,244.5,320.5
def bvh(o,ev=True):
    dg=bpy.context.evaluated_depsgraph_get()
    if ev:
        e=o.evaluated_get(dg); m=e.to_mesh(); b=BVHTree.FromPolygons([o.matrix_world@v.co for v in m.vertices],[tuple(p.vertices) for p in m.polygons]); e.to_mesh_clear(); return b
    return BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[tuple(p.vertices) for p in o.data.polygons])
def hz(b,x,y):
    h=b.ray_cast(Vector((x,y,500)),Vector((0,0,-1))); return h[0].z if h[0] is not None else None
rep={}
WB={n:bvh(O[n]) for n in WALKS if O.get(n)}
def wtop(x,y):
    zs=[hz(b,x,y) for b in WB.values()]; zs=[z for z in zs if z is not None]; return max(zs) if zs else None
def measure(tag):
    GB=[bvh(O[n]) for n in GRD]; c=0; tot=0; mx=0.0; where={}
    for x in np.arange(X0,X1,0.25):
        for y in np.arange(Y0,Y1,0.25):
            w=wtop(x,y)
            if w is None: continue
            tot+=1
            g=[hz(b,x,y) for b in GB]; g=[z for z in g if z is not None]
            if g and max(g)>w-0.005:
                c+=1; mx=max(mx,max(g)-w); k=(int(x)//5*5,int(y)//5*5); where[k]=where.get(k,0)+1
    rep['poke_walk_'+tag]=[c,tot,round(mx,3),sorted(where.items(),key=lambda t:-t[1])[:12]]
    print('WALKPOKE',tag,c,tot,round(mx,3),sorted(where.items(),key=lambda t:-t[1])[:8],flush=True)
measure('before')
for n in GRD:
    o=O[n]; me=o.data; mw=o.matrix_world; mi=mw.inverted()
    np.save(f'{R}/data/wv/{n[:12]}_pre_fix4.npy',np.array([v.co[:] for v in me.vertices]))
    a=0;b=0;mx=0.0
    for v in me.vertices:
        c=mw@v.co
        if not (X0<=c.x<=X1 and Y0<=c.y<=Y1): continue
        w0=wtop(c.x,c.y)
        if w0 is not None:
            if c.z>w0-0.03: d=c.z-(w0-0.03); c.z-=d; v.co=mi@c; a+=1; mx=max(mx,d)
            continue
        lo=None
        for dx,dy in ((0.7,0),(-0.7,0),(0,0.7),(0,-0.7),(0.5,0.5),(-0.5,0.5),(0.5,-0.5),(-0.5,-0.5)):
            w=wtop(c.x+dx,c.y+dy)
            if w is not None and (lo is None or w<lo): lo=w
        if lo is not None and c.z>lo-0.03:
            d=min(c.z-(lo-0.03),0.30); c.z-=d; v.co=mi@c; b+=1; mx=max(mx,d)
    me.update(); rep['lower_'+n[:12]]=[a,b,round(mx,3)]; print('LOWER',n[:12],a,b,round(mx,3),flush=True)
bpy.context.view_layer.update()
measure('after')
# grass: reseat in the tile AND in the unfeathered neighbour zones (WU x108-122, QW, WF south, WN/WO west 8 m)
GALL=GRD+['WU_richardson_reid_LiDAR_patch_UNVERIFIED','WF_east_dorm_LiDAR_terrain_patch_UNVERIFIED','WN_south_wood_LiDAR_patch_ext_UNVERIFIED','WO_gully_head_LiDAR_patch_UNVERIFIED']
GB=[bvh(O[n]) for n in GALL]
BOX=[(X0,X1,Y0,Y1),(105,122,238,330),(110,160,240,285),(110,165,312,330),(153,164,226,322)]
for name in ('QS_Richardson_lawn_grass_points_UNVERIFIED','QV_Richardson_NW_lawn_grass_points_UNVERIFIED'):
    o=O.get(name)
    if not o: continue
    me=o.data; mw=o.matrix_world; mi=mw.inverted(); k=0; dn=0; mx=0.0
    np.save(f'{R}/data/wv/{name[:2]}_grass_pre_fix4.npy',np.array([v.co[:] for v in me.vertices]))
    for v in me.vertices:
        c=mw@v.co
        if not any(b[0]<=c.x<=b[1] and b[2]<=c.y<=b[3] for b in BOX): continue
        g=[hz(b,c.x,c.y) for b in GB]; g=[z for z in g if z is not None]
        if not g: continue
        gz=max(g)
        if wtop(c.x,c.y) is not None:
            if c.z>gz-0.15: c.z=gz-0.2; v.co=mi@c; dn+=1
            continue
        if abs(c.z-gz)>0.02: mx=max(mx,abs(c.z-gz)); c.z=gz; v.co=mi@c; k+=1
    me.update(); rep['grass_'+name[:2]]=[k,dn,round(mx,3)]; print('GRASS',name[:2],k,dn,round(mx,3),flush=True)
r=json.load(open(f'{R}/data/wv/fix_report.json')); r['fix4']=rep
json.dump(r,open(f'{R}/data/wv/fix_report.json','w'),indent=1)
bpy.ops.wm.save_mainfile(); print('SAVED',flush=True)
