# W59c (ws242): probe242c_w57c: in the W57 eye view the dark band = camera rays passing UNDER M3b's free edges (the SE island
# x -380..-360, y -52..-21 and the edge pieces by the police terrace) and hitting the skirt 1.2-1.5 m below, where
# WS235_skirt_under_M3b_corridor holds it under M3b. v1 (straight-down 1.6 m curtain) read as a pale 1.3 m wall in the test
# render -> v2: sloped lawn flap = each edge extruded 4 m outward (per-edge outward dir) down to the RAW (base-mesh) skirt
# there - 0.05, so low views see a graded bank instead of the dark slot under the tile. UNVERIFIED design (fill bank).
# Only M3b boundary edges in x -397..-345, y -56..-17 whose outside (0.6 m out) is not covered by another ground mesh
# (WS68/PK/WS60/terrain base meshes). Ground only; no paving touched; nothing raised or lowered.
import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
o=next(x for x in bpy.data.objects if x.name.startswith('M3b_north_LiDAR_DTM_1m'))
M=o.matrix_world; Mi=M.inverted()
G=[x for x in bpy.data.objects if x.type=='MESH' and x.name.startswith(('WS68_RHD_ground','PK_Feliciano','WS60_terrain','Terrain_LiDAR_DTM_1m','PZ_Feliciano'))]
BV=[BVHTree.FromPolygons([(g.matrix_world@v.co)[:] for v in g.data.vertices],[p.vertices[:] for p in g.data.polygons]) for g in G if g.data.polygons]
def cov(p): return any(t.ray_cast(Vector((p.x,p.y,600)),Vector((0,0,-1)))[0] for t in BV)
bm=bmesh.new(); bm.from_mesh(o.data); bm.edges.ensure_lookup_table()
E=[]
for e in bm.edges:
    if not e.is_boundary: continue
    a=M@e.verts[0].co; b=M@e.verts[1].co; m=(a+b)/2
    if not (-397<=m.x<=-345 and -56<=m.y<=-17): continue
    fc=M@e.link_faces[0].calc_center_median(); d=Vector((m.x-fc.x,m.y-fc.y,0)).normalized()
    if cov(m+d*0.6): continue
    E.append(e)
SK=bpy.data.objects['Context_skirt_3DEP_ortho_4km']; SW=SK.matrix_world
TS=BVHTree.FromPolygons([(SW@v.co)[:] for v in SK.data.vertices],[p.vertices[:] for p in SK.data.polygons])
DIR={}
for e in E:
    a=M@e.verts[0].co; b=M@e.verts[1].co; fc=M@e.link_faces[0].calc_center_median(); d=Vector((((a+b)/2-fc).x,((a+b)/2-fc).y,0)).normalized()
    for v in e.verts: DIR.setdefault(v.index,[]).append(d)
pos={tuple(round(c,5) for c in v.co):v.index for e in E for v in e.verts}
r=bmesh.ops.extrude_edge_only(bm,edges=E)
nv=[g for g in r['geom'] if isinstance(g,bmesh.types.BMVert)]
mx=0
for v in nv:
    i=pos.get(tuple(round(c,5) for c in v.co))
    if i is None: continue
    d=sum(DIR[i],Vector()); d=d.normalized() if d.length>1e-6 else Vector((0,-1,0))
    p=M@v.co; q=Vector((p.x+d.x*4,p.y+d.y*4,0))
    h=TS.ray_cast(Vector((q.x,q.y,600)),Vector((0,0,-1)))
    z=(h[0].z-0.05) if h[0] else p.z-1.0
    z=min(z,p.z-0.05); mx=max(mx,p.z-z)
    v.co=Mi@Vector((q.x,q.y,z))
bm.normal_update()
nf=[g for g in r['geom'] if isinstance(g,bmesh.types.BMFace)]
bm.to_mesh(o.data); o.data.update(); bm.free()
print('F242D M3b flap edges',len(E),'max drop',round(mx,2),'new verts',len(nv),'faces',len(nf),flush=True)
