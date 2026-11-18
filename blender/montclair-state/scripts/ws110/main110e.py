# ws110 ground layer: fine 1 m terrain patch from the 2023 DTM (ws79 grid) S of the main terrain edge (y -250),
# capped under the new paving; skirt pushed under it. Plus the brick crosswalk band (main110d).
import bpy, bmesh, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R='/workspace/nj-scenes/montclair-state/'
D=np.load(R+'prep/ws79_normal_ave_dtm/normal_ave_dtm_1m.npz'); DT=D['dtm']; DX0=float(D['x0']); DY0=float(D['y0'])
def dtm(x,y):
    fx=x-DX0; fy=y-DY0; j=int(np.floor(fx)); i=int(np.floor(fy))
    j=min(max(j,0),DT.shape[1]-2); i=min(max(i,0),DT.shape[0]-2); a=fx-j; b=fy-i
    return float(DT[i,j]*(1-a)*(1-b)+DT[i,j+1]*a*(1-b)+DT[i+1,j]*(1-a)*b+DT[i+1,j+1]*a*b)
def obvh(o):
    bm=bmesh.new(); bm.from_mesh(o.data); bm.transform(o.matrix_world); t=BVHTree.FromBMesh(bm); bm.free(); return t
coll=bpy.data.collections['WS110_CollegeAve_S_end_NormalAve_road_layer']
pave=[o for o in coll.objects if o.type=='MESH']
# also existing paving reaching S of -249 (WS102 end, walks)
for o in bpy.data.objects:
    if o.type!='MESH' or o.hide_render or o in pave: continue
    if o.name.startswith(('WS102','WS103','WS104','Footpaths')):
        bb=[o.matrix_world@Vector(c) for c in o.bound_box]
        if min(v.y for v in bb)<-246: pave.append(o)
print('E110e pave',[o.name for o in pave])
PB=[obvh(o) for o in pave]
def pz(x,y):
    zs=[]
    for t in PB:
        h=t.ray_cast(Vector((x,y,300)),Vector((0,0,-1)))[0]
        if h is not None: zs.append(h.z)
    return min(zs) if zs else None
X0,X1,Y0,Y1=-300.0,-150.0,-300.0,-249.0
xs=np.arange(X0,X1+0.01,1.0); ys=np.arange(Y0,Y1+0.01,1.0)
TB=obvh(bpy.data.objects['Terrain_LiDAR_DTM_1m'])
bm=bmesh.new(); G=[]; capn=0
for y in ys:
    r=[]
    for x in xs:
        z=dtm(x,y)
        if y>=Y1-0.01:  # snap the N row onto the existing terrain edge where it exists
            h=TB.ray_cast(Vector((x,y+0.3,300)),Vector((0,0,-1)))[0]
            if h is not None: z=h.z
        best=None
        for dx in (-0.7,0,0.7):
            for dy in (-0.7,0,0.7):
                p=pz(x+dx,y+dy)
                if p is not None: best=p if best is None else min(best,p)
        if best is not None and z>best-0.08: z=best-0.08; capn+=1
        r.append(bm.verts.new((x,y,z)))
    G.append(r)
for i in range(len(ys)-1):
    for j in range(len(xs)-1): bm.faces.new((G[i][j],G[i][j+1],G[i+1][j+1],G[i+1][j]))
me=bpy.data.meshes.new('WS110_ground_patch'); bm.to_mesh(me); bm.free()
me.materials.append(bpy.data.materials['COLE_lawn_post2020_bs'])
for p in me.polygons: p.use_smooth=True
gp=bpy.data.objects.new('WS110_ground_patch_S_of_y-249_DTM2023_1m_lawn_UNVERIFIED',me); coll.objects.link(gp)
print('E110e patch verts',len(me.vertices),'capped',capn)
# skirt + main terrain: anything above the patch inside its footprint goes 0.3 m under the DTM
for tn in ('Context_skirt_3DEP_ortho_4km','Terrain_LiDAR_DTM_1m'):
    t=bpy.data.objects[tn]; mw=t.matrix_world; inv=mw.inverted(); n=0
    for v in t.data.vertices:
        w=mw@v.co
        if X0<=w.x<=X1 and Y0<=w.y<-249.5:
            zt=dtm(w.x,w.y)-0.30
            p=pz(w.x,w.y)
            if p is not None: zt=min(zt,p-0.15)
            if w.z>zt: v.co=inv@Vector((w.x,w.y,zt)); n+=1
    t.data.update(); print('E110e',tn,'pushed under',n)
# probe: patch above paving?
GB=obvh(gp); pokes=0; worst=0
for o in pave:
    for v in o.data.vertices:
        w=o.matrix_world@v.co
        h=GB.ray_cast(Vector((w.x,w.y,300)),Vector((0,0,-1)))[0]
        if h is not None and h.z>w.z-0.03: pokes+=1; worst=max(worst,h.z-w.z)
print('P110e patch over paving',pokes,'worst %.2f'%worst)
exec(open(R+'scripts/ws110/main110d.py').read())
