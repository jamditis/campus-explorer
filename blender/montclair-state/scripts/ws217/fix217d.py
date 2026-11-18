# ws217 W38: at the walk's E end, between the WS72 Kasser landing's ragged N edge (y -47.5..-46.8), the stair tower's E face and the
# Kasser arcade lobby/end wall, the draped WS68 north-DTM ground (tan ortho tone) shows as a ~6 x 3 m patch (subset ray probe
# probe217e.py, terrain GN on). A pedestrian gap between a stair-tower door and a lobby door off a paved landing is paved; the tan
# ground is a modelling gap, not lawn (no lawn there in the 2020 ortho by eye; finish UNVERIFIED). Rev 2: fill it with one concrete
# surface on a 0.25 m grid over the cells where the top hit is WS68 (cells under a roof/eave are skipped automatically), each vertex
# at max(WS68 + 2 cm, the landing's edge grade at that x) so it continues the landing level to the walls (paving raised, never lowered).
import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
def ob(p): return next((o for o in bpy.data.objects if o.name.startswith(p)),None)
L=ob('WS72_Kasser_SW_RHD_core_sidewalk_landing'); G=ob('WS68_RHD_ground_northDTM')
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
def bvh(o,top=False):
    M=o.matrix_world; P=[p for p in o.data.polygons if (not top) or (M.to_3x3()@p.normal).z>0.7]
    return BVHTree.FromPolygons([M@v.co for v in o.data.vertices],[p.vertices[:] for p in P])
TL=bvh(L,top=True); TG=bvh(G,top=True)
OCC=[o for o in bpy.data.objects if o.type=='MESH' and o.visible_get() and o.name!=G.name and not o.name.startswith(('Terrain','WS60','Context','BD_','WS67_','WS73_','WS72_cut')) ]
def bb(o):
    c=[o.matrix_world@Vector(k) for k in o.bound_box]; return min(v.x for v in c),max(v.x for v in c),min(v.y for v in c),max(v.y for v in c)
OCC=[o for o in OCC if (lambda b: b[1]>-256 and b[0]<-247.5 and b[3]>-48.5 and b[2]<-43.5)(bb(o))]
TO=[(o.name,bvh(o)) for o in OCC]
def tophit(x,y):
    best=(None,-1e9)
    for n,t in TO:
        h=t.ray_cast(Vector((x,y,160)),Vector((0,0,-1)),60)
        if h[0] is not None and h[0].z>best[1]: best=(n,h[0].z)
    return best
def zg(x,y):
    h=TG.ray_cast(Vector((x,y,200)),Vector((0,0,-1)),300); return h[0].z if h[0] is not None else None
def zl_edge(x,y):
    for k in range(0,16):
        h=TL.ray_cast(Vector((x,y-0.1*k,200)),Vector((0,0,-1)),300)
        if h[0] is not None: return h[0].z
    return None
DX0,DX1,DY0,DY1,DS=-255.75,-247.75,-48.0,-43.75,0.25
nx=int(round((DX1-DX0)/DS)); ny=int(round((DY1-DY0)/DS))
import json, os
CF='/workspace/nj-scenes/montclair-state/scripts/ws217/w38_cells.json'
if os.path.exists(CF):
    cells=set(tuple(c) for c in json.load(open(CF)))
else:
    # first (subset, terrain GN on) run: a cell is a gap if the evaluated scene's first hit from above is the WS68 ground;
    # the cell list is frozen to w38_cells.json so the low-memory merge (modifiers off) builds the identical surface.
    cells=set()
    for i in range(nx):
        for j in range(ny):
            cx,cy=DX0+(i+0.5)*DS,DY0+(j+0.5)*DS
            r=sc.ray_cast(dg,Vector((cx,cy,160)),Vector((0,0,-1)))
            if r[0] and r[4].name.startswith('WS68_RHD_ground_northDTM'): cells.add((i,j))
    json.dump(sorted(cells),open(CF,'w'))
me=bpy.data.meshes.new('WS217_RHD_SE_Kasser_gap_paving'); bm=bmesh.new(); V={}
def vert(i,j):
    if (i,j) not in V:
        x,y=DX0+i*DS,DY0+j*DS; g=zg(x,y) or 125.3; zl=zl_edge(x,y)
        V[(i,j)]=bm.verts.new((x,y,max(g+0.02,zl if zl is not None and zl<g+0.25 else g+0.02)))
    return V[(i,j)]
for i,j in cells: bm.faces.new((vert(i,j),vert(i+1,j),vert(i+1,j+1),vert(i,j+1)))
bm.to_mesh(me); bm.free()
me.materials.append(bpy.data.materials.get('Kasser_apron_concrete_cm'))
o=bpy.data.objects.new('WS217_RHD_SE_Kasser_gap_paving_UNVERIFIED_finish',me)
for c in L.users_collection: c.objects.link(o)
print('F217d gap paving cells',len(cells),'verts',len(V),flush=True)
