# ws206 W25: faint dark crease where the smoothed WS98 Kasser-east entry aisle meets the accessible/Sprague lot asphalt to its W
# (x ~ -215.1, y -68..-86). probe206: the aisle's W edge sits 3-13 cm BELOW the lot (WS76 overlaps it by 0.2 m and is on top),
# so the lot edge casts a small step = the dark crease. Fix (raise-only, lower side up): sample the lot height at every aisle
# boundary vertex (lot hit at the vertex or within 0.5 m), required lift = lot+3 mm - aisle (only gaps 0..0.25 m, so curbs are
# ignored), spread as a smoothstep cone over 2.5 m to aisle verts and to the WS205 apron fill (same field, so the aisle/fill
# joint keeps its 4 mm tuck); capped 4 mm under every other surface (curbs, pad, road, islands).
import bpy, bmesh, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
def ob(p): return [o for o in bpy.data.objects if o.name.startswith(p)][0]
def bvh(o):
    mw=o.matrix_world; return BVHTree.FromPolygons([mw@v.co for v in o.data.vertices],[tuple(p.vertices) for p in o.data.polygons])
def hz(t,x,y):
    h=t.ray_cast(Vector((x,y,160)),Vector((0,0,-1)),80); return h[0].z if h[0] is not None else None
AI=ob('WS98_lotE_entry_aisle'); FI=ob('WS205_lotE_entry_apron')
LOTN=['WS76_accessible_lot_asphalt','WS75_sprague_lot_asphalt','WS79_lot_E_patch','WS96_lot_E_edge_gap','WS94_lot_slit_filler']
LT=[bvh(ob(n)) for n in LOTN]
OTN=['WS98_CollegeAve_bend_teardrop_island_CURB','WS98_CollegeAve_bend_teardrop_island_MULCH','WS98_lotE_raised_concrete_walk_pad','WS27_CollegeAve_carriageway','WS27_CollegeAve_curb_right','WS99_lotE_padS_bed','Footpaths_OSM','WS77_lot_median_island_MULCH','WS76_lot_stall_paint_blue']
OT=[bvh(ob(n)) for n in OTN]
def lotz(x,y):
    best=None
    for r in (0,0.15,0.3,0.5):
        for a in np.linspace(0,2*np.pi,9)[:-1] if r>0 else [0]:
            for t in LT:
                z=hz(t,x+r*np.cos(a),y+r*np.sin(a))
                if z is not None: best=z if best is None else max(best,z)
        if best is not None: return best
    return None
bm=bmesh.new(); bm.from_mesh(AI.data); bm.verts.ensure_lookup_table()
mw=AI.matrix_world; B=[]
for v in bm.verts:
    if v.is_boundary:
        g=mw@v.co; zl=lotz(g.x,g.y)
        if zl is not None and 0 < zl+0.003-g.z < 0.25: B.append((g.x,g.y,zl+0.003-g.z))
bm.free(); B=np.array(B); print('F206a boundary sources',len(B),'max req %.3f'%(B[:,2].max() if len(B) else 0),flush=True)
R=2.5
def lift(x,y):
    d=np.sqrt((B[:,0]-x)**2+(B[:,1]-y)**2); f=np.clip(1-d/R,0,1); f=f*f*(3-2*f); return float((B[:,2]*f).max())
def apply(o,tuck):
    mw=o.matrix_world; mi=mw.inverted(); n=0; mx=0
    TA=bvh(AI) if tuck else None
    for v in o.data.vertices:
        g=mw@v.co; L=lift(g.x,g.y)
        if L<=0: continue
        z=g.z+L
        for t in OT:
            zo=hz(t,g.x,g.y)
            if zo is not None and zo>g.z and zo<z+0.004: z=max(g.z,zo-0.004)
        if tuck:
            za=hz(TA,g.x,g.y)
            if za is not None and z>za-0.004: z=max(g.z,za-0.004)
        if z>g.z: mx=max(mx,z-g.z); g.z=z; v.co=mi@g; n+=1
    o.data.update(); print('F206a',o.name[:30],'verts lifted',n,'max %.3f'%mx,flush=True)
apply(AI,False); apply(FI,True)
