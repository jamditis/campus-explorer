# W53i (ws229, found in the W53g close-up self-review): north of A2 the WS60 edge apron's east band (x 246..276) was not a
# strip at all: a few giant diagonal faces (~1,400 m2 each) ran from the A2 row (y -33.5) to the NE corner (216, 263..278),
# plus one 1 m row at y -6..-5, so a slanted sheet stood 1.5-6 m over the LiDAR across the whole east edge. Those faces
# (apron faces spanning > 100 m in y, and the y -6..-5 row with centre x > 238) are deleted and the band is rebuilt as a
# regular strip: rows every 4 m from y -33.5 to 248 (the QI LiDAR patch's north limit), columns x 246 / 253.5 / 261 /
# 268.5 / 276; inner z = top of the QI LiDAR patch at x 245.9 (else dtm_1m), outer z = top of the 4 km skirt/far field at
# x 276 + 2 cm, middle columns linear. UVs from WS60's own affine map. The NE corner square (x 246..276, y 248..278) is left
# as is (UNVERIFIED; the skirt shows there). NOTE: north of y ~70 dtm_1m is edge-padded (constant rows) and the QI patch
# follows it, so the inner edge there is up to ~8 m over USGS 3DEP and the strip falls steeply to the skirt (W53j, open).
import bpy, bmesh, json, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
A=np.load('/workspace/nj-scenes/montclair-state/data/dtm_1m.npy')
def dtm(x,y):
    gx=min(249.49,x)+250-0.5; gy=min(249.49,y)+250-0.5; i=int(np.floor(gy)); j=int(np.floor(gx)); fy=gy-i; fx=gx-j
    i=min(498,max(0,i)); j=min(498,max(0,j))
    return float(A[i,j]*(1-fx)*(1-fy)+A[i,j+1]*fx*(1-fy)+A[i+1,j]*(1-fx)*fy+A[i+1,j+1]*fx*fy)
ap=bpy.data.objects['WS60_terrain_edge_apron_LiDAR_to_skirt']; me=ap.data; W=ap.matrix_world; inv=W.inverted()
qi=bpy.data.objects['QI_east_edge_LiDAR_terrain_patch']; QW=qi.matrix_world
BQ=BVHTree.FromPolygons([QW@v.co for v in qi.data.vertices],[p.vertices[:] for p in qi.data.polygons])
dg=bpy.context.evaluated_depsgraph_get(); BS=[]
for nm in ('Context_skirt_3DEP_ortho_4km','BD_farfield_3DEP_ortho'):
    o=bpy.data.objects[nm]
    for m in o.modifiers: m.show_viewport=m.show_render
dg.update()
for nm in ('Context_skirt_3DEP_ortho_4km','BD_farfield_3DEP_ortho'):
    o=bpy.data.objects[nm]; e=o.evaluated_get(dg); mm=e.to_mesh(); OW=o.matrix_world
    BS.append(BVHTree.FromPolygons([OW@v.co for v in mm.vertices],[p.vertices[:] for p in mm.polygons])); e.to_mesh_clear()
def rz(B,x,y):
    h=B.ray_cast(Vector((x,y,400)),Vector((0,0,-1))); return None if h[0] is None else h[0].z
# UV affine from WS60's own loops (before edits)
L=me.uv_layers.active; X=[];U=[]
for lp in me.loops:
    w=W@me.vertices[lp.vertex_index].co; X.append((w.x,w.y,1)); U.append(L.data[lp.index].uv[:])
X=np.array(X);U=np.array(U); cu=np.linalg.lstsq(X,U[:,0],rcond=None)[0]; cv=np.linalg.lstsq(X,U[:,1],rcond=None)[0]
uvres=float(max(np.abs(X@cu-U[:,0]).max(),np.abs(X@cv-U[:,1]).max()))
bm=bmesh.new(); bm.from_mesh(me); uvl=bm.loops.layers.uv.active
dele=[]
for f in bm.faces:
    ws=[W@v.co for v in f.verts]; ys=[w.y for w in ws]; c=sum(ws,Vector())/len(ws)
    if max(ys)-min(ys)>100 and max(w.x for w in ws)>240: dele.append(f)
    elif c.x>238 and -6.01<=min(ys) and max(ys)<=-4.99: dele.append(f)
info=[(f.index,round(f.calc_area())) for f in dele]
mat=dele[0].material_index if dele else 0
bmesh.ops.delete(bm,geom=dele,context='FACES')
XS=[246.0,253.5,261.0,268.5,276.0]
YS=list(np.arange(-33.5,248.0,4.0))+[248.0]
# reuse existing A2-row verts at y -33.5 so the strip welds to the ws228 south part
ex={}
for v in bm.verts:
    w=W@v.co
    if abs(w.y+33.5)<0.05 and w.x>244: ex[min(XS,key=lambda x:abs(x-w.x))]=v
grid=[]; zin=[]; zout=[]
for y in YS:
    zi=rz(BQ,245.9,y); zi=dtm(245.9,y) if zi is None else zi
    zs=[z for z in (rz(B,276.0,y) for B in BS) if z is not None]; zo=(max(zs)+0.02) if zs else zi
    zin.append(zi-dtm(245.9,y)); zout.append(zo-zi)
    row=[]
    for x in XS:
        if abs(y+33.5)<1e-6 and x in ex: row.append(ex[x]); continue
        z=zi+(zo-zi)*(x-246.0)/30.0
        row.append(bm.verts.new(inv@Vector((x,y,z))))
    grid.append(row)
nf=0; newf=[]
for a,b in zip(grid[:-1],grid[1:]):
    for k in range(4):
        try:
            f=bm.faces.new((a[k],a[k+1],b[k+1],b[k])); f.material_index=mat; nf+=1; newf.append(f)
            for l in f.loops:
                w=W@l.vert.co; l[uvl].uv=(cu[0]*w.x+cu[1]*w.y+cu[2], cv[0]*w.x+cv[1]*w.y+cv[2])
        except ValueError: pass
lo=[v for v in bm.verts if not v.link_edges]; bmesh.ops.delete(bm,geom=lo,context='VERTS')
bm.normal_update()
for f in newf:
    if (W.to_3x3()@f.normal).z<0: f.normal_flip()
bm.normal_update()
up=sum(1 for f in newf if (W.to_3x3()@f.normal).z<0)
bm.to_mesh(me); bm.free(); me.update()
rep={'deleted':info,'new_faces':nf,'rows':len(YS),'reused_A2_row':sorted(ex.keys()),'inner_vs_dtm':[round(min(zin),2),round(max(zin),2)],'outer_minus_inner':[round(min(zout),2),round(max(zout),2)],'down_faces_after':up,'uv_fit_res':round(uvres,5)}
print('F229G',json.dumps(rep),flush=True)
json.dump(rep,open('/workspace/nj-scenes/montclair-state/scripts/ws229/fix229g_report.json','w'))
