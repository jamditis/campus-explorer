# W53h (ws229): south scene edge of the SE corner. probe229h: past the terrain's south boundary (y ~ -249, x 95..246) there is
# no apron (WS60 has only a loose edge there); the band is the 4 km USGS 3DEP skirt sitting 0.4-1.2 m under the terrain edge,
# so the edge reads as a lip. Same treatment as the WS60 east apron: a 3-row strip from each terrain south-boundary vertex
# (exact xyz, watertight in xy) straight south to y = -262, heights linear to the top of the skirt/far-field there (+2 cm).
# Material/UV mapping copied from WS60_terrain_edge_apron_LiDAR_to_skirt (affine fit of its own UVs). UNVERIFIED surface tone.
import bpy, bmesh, json, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
t=bpy.data.objects['Terrain_LiDAR_DTM_1m']; me=t.data; M=t.matrix_world
ap=bpy.data.objects['WS60_terrain_edge_apron_LiDAR_to_skirt']
dg=bpy.context.evaluated_depsgraph_get()
B=[]
for nm in ('Context_skirt_3DEP_ortho_4km','BD_farfield_3DEP_ortho'):
    o=bpy.data.objects[nm]
    for m in o.modifiers: m.show_viewport=m.show_render
dg.update()
for nm in ('Context_skirt_3DEP_ortho_4km','BD_farfield_3DEP_ortho'):
    o=bpy.data.objects[nm]; e=o.evaluated_get(dg); mm=e.to_mesh(); W=o.matrix_world
    B.append(BVHTree.FromPolygons([W@v.co for v in mm.vertices],[p.vertices[:] for p in mm.polygons])); e.to_mesh_clear()
def top(x,y):
    zs=[h[0].z for b in B for h in [b.ray_cast(Vector((x,y,400)),Vector((0,0,-1)))] if h[0] is not None]
    return max(zs) if zs else None
bm=bmesh.new(); bm.from_mesh(me)
ed=[e for e in bm.edges if e.is_boundary and all(v.co.y<-247.5 and 95<=v.co.x<=246.35 for v in e.verts)]
vs=sorted({v for e in ed for v in e.verts},key=lambda v:v.co.x)
pts=[(M@v.co) for v in vs]; bm.free()
YO=-262.0
rows=[]
for p in pts:
    zo=top(p.x,YO); zo=(p.z if zo is None else zo+0.02)
    rows.append([Vector((p.x,p.y,p.z)),Vector((p.x,(p.y*2+YO)/3,(p.z*2+zo)/3)),Vector((p.x,(p.y+YO*2)/3,(p.z+zo*2)/3)),Vector((p.x,YO,zo))])
# affine UV fit of WS60's own loops
am=ap.data; L=am.uv_layers.active
X=[];U=[]
for lp in am.loops:
    w=ap.matrix_world@am.vertices[lp.vertex_index].co; X.append((w.x,w.y,1)); U.append(L.data[lp.index].uv[:])
X=np.array(X);U=np.array(U); cu=np.linalg.lstsq(X,U[:,0],rcond=None)[0]; cv=np.linalg.lstsq(X,U[:,1],rcond=None)[0]
res=float(max(np.abs(X@cu-U[:,0]).max(),np.abs(X@cv-U[:,1]).max()))
nm='WS229_SE_south_edge_apron_UNVERIFIED'
old=bpy.data.objects.get(nm)
if old: bpy.data.objects.remove(old)
nme=bpy.data.meshes.new(nm); bmo=bmesh.new()
V=[[bmo.verts.new(c) for c in r] for r in rows]
for i in range(len(V)-1):
    for k in range(3):
        f=bmo.faces.new((V[i][k],V[i+1][k],V[i+1][k+1],V[i][k+1]))
bmo.normal_update()
for f in bmo.faces:
    if f.normal.z<0: f.normal_flip()
uvl=bmo.loops.layers.uv.new(L.name)
for f in bmo.faces:
    for l in f.loops:
        c=l.vert.co; l[uvl].uv=(cu[0]*c.x+cu[1]*c.y+cu[2], cv[0]*c.x+cv[1]*c.y+cv[2])
bmo.to_mesh(nme); bmo.free()
for s in ap.data.materials: nme.materials.append(s)
for p in nme.polygons: p.use_smooth=False
o=bpy.data.objects.new(nm,nme)
for c in ap.users_collection: c.objects.link(o)
drop=[round(r[0].z-r[3].z,2) for r in rows]
rep={'edge_verts':len(pts),'x':[round(pts[0].x,1),round(pts[-1].x,1)] if pts else None,'faces':len(nme.polygons),'drop_m':[min(drop),max(drop)] if drop else None,'uv_fit_res':round(res,5),'collections':[c.name for c in ap.users_collection]}
print('F229E',json.dumps(rep),flush=True)
json.dump(rep,open('/workspace/nj-scenes/montclair-state/scripts/ws229/fix229e_report.json','w'))
