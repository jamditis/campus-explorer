# ws110 seam fix: rebuild the DTM patch N to y -238 (fills the terrain hole W of College Ave, tucks 5 cm under the terrain edge),
# cap it under every non-tree mesh, push apron/skirt under it.
import bpy, bmesh, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R='/workspace/nj-scenes/montclair-state/'
D=np.load(R+'prep/ws79_normal_ave_dtm/normal_ave_dtm_1m.npz'); DT=D['dtm']; DX0=float(D['x0']); DY0=float(D['y0'])
DM=np.load(R+'data/dtm_1m.npy') if False else None
def dtm(x,y):
    fx=x-DX0; fy=y-DY0; j=int(np.floor(fx)); i=int(np.floor(fy))
    j=min(max(j,0),DT.shape[1]-2); i=min(max(i,0),DT.shape[0]-2); a=fx-j; b=fy-i
    return float(DT[i,j]*(1-a)*(1-b)+DT[i,j+1]*a*(1-b)+DT[i+1,j]*(1-a)*b+DT[i+1,j+1]*a*b)
def obvh(o):
    bm=bmesh.new(); bm.from_mesh(o.data); bm.transform(o.matrix_world); t=BVHTree.FromBMesh(bm); bm.free(); return t
old=bpy.data.objects['WS110_ground_patch_S_of_y-249_DTM2023_1m_lawn_UNVERIFIED']; mat=old.data.materials[0]; coll=old.users_collection[0]
bpy.data.objects.remove(old)
X0,X1,Y0,Y1=-300.0,-150.0,-300.0,-238.0
skip=('T_','Terrain_','Context_','WS60_terrain_edge_apron','WS110_ground')
objs=[]
for o in bpy.data.objects:
    if o.type!='MESH' or o.hide_render or o.name.startswith(skip): continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    if max(v.x for v in bb)<X0 or min(v.x for v in bb)>X1 or max(v.y for v in bb)<Y0 or min(v.y for v in bb)>Y1: continue
    if (max(v.x for v in bb)-min(v.x for v in bb))>600: continue
    objs.append(o)
print('E110g cap objs',len(objs))
OB=[obvh(o) for o in objs]; TB=obvh(bpy.data.objects['Terrain_LiDAR_DTM_1m'])
def capz(x,y):
    best=None
    for t in OB:
        h=t.ray_cast(Vector((x,y,300)),Vector((0,0,-1)))[0]
        if h is not None: best=h.z if best is None else min(best,h.z)
    return best
xs=np.arange(X0,X1+0.01,1.0); ys=np.arange(Y0,Y1+0.01,1.0)
bm=bmesh.new(); G=[]; nt=nc=0
for y in ys:
    r=[]
    for x in xs:
        z=dtm(x,y)
        h=TB.ray_cast(Vector((x,y,300)),Vector((0,0,-1)))[0]
        if h is not None: z=h.z-0.05; nt+=1
        else:
            # near the terrain edge: follow it (avoid a step) -- sample 1.2 m north
            h2=TB.ray_cast(Vector((x,y+1.2,300)),Vector((0,0,-1)))[0]
            if h2 is not None: z=0.5*(z+h2.z)
        best=None
        for dx,dy in ((0,0),(-0.6,0),(0.6,0),(0,-0.6),(0,0.6)):
            c=capz(x+dx,y+dy)
            if c is not None: best=c if best is None else min(best,c)
        if best is not None and z>best-0.08: z=best-0.08; nc+=1
        r.append(bm.verts.new((x,y,z)))
    G.append(r)
for i in range(len(ys)-1):
    for j in range(len(xs)-1): bm.faces.new((G[i][j],G[i][j+1],G[i+1][j+1],G[i+1][j]))
me=bpy.data.meshes.new('WS110_ground_patch'); bm.to_mesh(me); bm.free(); me.materials.append(mat)
for p in me.polygons: p.use_smooth=True
gp=bpy.data.objects.new('WS110_ground_patch_S_of_y-238_DTM2023_1m_lawn_UNVERIFIED',me); coll.objects.link(gp)
print('E110g patch verts',len(me.vertices),'under-terrain',nt,'capped',nc)
GB=obvh(gp)
for tn in ('WS60_terrain_edge_apron_LiDAR_to_skirt','Context_skirt_3DEP_ortho_4km'):
    t=bpy.data.objects[tn]; mw=t.matrix_world; inv=mw.inverted(); n=0
    for v in t.data.vertices:
        w=mw@v.co
        if X0<=w.x<=X1 and Y0<=w.y<=Y1-0.5:
            h=GB.ray_cast(Vector((w.x,w.y,300)),Vector((0,0,-1)))[0]
            if h is not None and w.z>h.z-0.30: v.co=inv@Vector((w.x,w.y,h.z-0.30)); n+=1
    t.data.update(); print('E110g',tn,'pushed',n)
bpy.ops.wm.save_mainfile(); print('M110 SAVED g',flush=True)
exec(open(R+'scripts/ws105/cut105.py').read().replace('ws105/render_cut105','ws110/render_cut110'))
