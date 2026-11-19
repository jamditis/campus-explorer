# W53m (ws230, found by the Q6 paving check probe230i, pre-existing since ws228): at the SE east edge the street that runs
# off the scene (Roads_OSM, x 245..250, y -38..-20) is 0.1-0.8 m UNDER the WS60 apron strip / terrain edge. Paving is not
# lowered (AGENTS rule 6): WS60 apron verts in x 243..258, y -42..-16 that lie under that road (ray hit within the road
# footprint, sampled at the vert and 1.5 m around it; faces subdivided first) and stand above road - 0.05 are tucked to road - 0.05.
import bpy, json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
r=bpy.data.objects['Roads_OSM']; RW=r.matrix_world
BR=BVHTree.FromPolygons([RW@v.co for v in r.data.vertices],[p.vertices[:] for p in r.data.polygons])
def rz(x,y):
    zs=[]
    for dx,dy in ((0,0),(1.5,0),(-1.5,0),(0,1.5),(0,-1.5)):
        h=BR.ray_cast(Vector((x+dx,y+dy,400)),Vector((0,0,-1)))
        if h[0] is not None: zs.append(h[0].z)
    return min(zs) if zs else None
ap=bpy.data.objects['WS60_terrain_edge_apron_LiDAR_to_skirt']; W=ap.matrix_world; I=W.inverted()
# the strip faces are 7.5 m wide, so the road edge falls mid-face: first subdivide the faces in x 244..256, y -42..-16
# (3 cuts per edge, UVs interpolated; WS60's UV map is affine so interpolation is exact), then tuck
import bmesh
bm=bmesh.new(); bm.from_mesh(ap.data); nf0=len(bm.faces)
fs=[f for f in bm.faces if all(244<=(W@v.co).x<=256 and -42<=(W@v.co).y<=-16 for v in f.verts)]
es=list({e for f in fs for e in f.edges})
bmesh.ops.subdivide_edges(bm,edges=es,cuts=3,use_grid_fill=True)
bm.to_mesh(ap.data); bm.free(); ap.data.update(); nsub=len(ap.data.polygons)-nf0
mv=[]
for v in ap.data.vertices:
    w=W@v.co
    if not (243<=w.x<=258 and -42<=w.y<=-16): continue
    z=rz(w.x,w.y)
    if z is None or w.z<=z-0.05: continue
    mv.append((round(w.x,1),round(w.y,1),round(w.z-(z-0.05),2))); w.z=z-0.05; v.co=I@w
ap.data.update()
rep={'faces_subdivided':len(fs),'faces_added':nsub,'apron_verts_tucked':len(mv),'moves':mv[:40]}
print('F230E',json.dumps(rep),flush=True)
json.dump(rep,open('/workspace/nj-scenes/montclair-state/scripts/ws230/fix230e_report.json','w'))
