# ws145 (UNIFY #50 part 3): Skyline W walk N end = rounded curb nose at y ~ -206.2, lot asphalt runs to it.
# Evidence (2023 LiDAR class-2 intensity, dtm142.npy layer 2, 0.5 m): asphalt 2-3k continuous x -72..-64 down to y -206.0;
# walk concrete (older, 5.5-7k) x -72..-71 from y -206.5 S; bright new curb concrete (8-11k) starts (-70.5,-207.0) and runs SSE
# (-70.0,-208.0) (-69.5,-209.0) (-69.0,-210.5) (-68.5,-211.5); asphalt E of it. W of x -72.5 = WS141 pad concrete (11-13k).
# Runs AFTER comb143 (needs WS142 lot) on montclair_state_ws143a.blend; OUT env saves a copy. Curb section/reveal UNVERIFIED.
import bpy, bmesh, os, math, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
OUT=os.environ.get('OUT',''); OB=bpy.data.objects
W='/workspace/nj-scenes/montclair-state/scripts/ws142/'
DD=np.load(W+'dtm142.npy'); ZS=DD[1]; X0,Y1,R=-95.0,-162.0,0.5
def dz(x,y):
    fi=(x-X0)/R; fj=(Y1-y)/R
    i=int(min(max(math.floor(fi),0),ZS.shape[1]-2)); j=int(min(max(math.floor(fj),0),ZS.shape[0]-2)); tx=min(max(fi-i,0),1); ty=min(max(fj-j,0),1)
    return float(ZS[j,i]*(1-tx)*(1-ty)+ZS[j,i+1]*tx*(1-ty)+ZS[j+1,i]*(1-tx)*ty+ZS[j+1,i+1]*tx*ty)
def lz(x,y): return dz(x,y)+0.04
XW,XE,YTOP=-72.9,-68.25,-202.8
# nose line (walk side = W/S). Rounded N-end corner: Chaikin-smoothed.
P=[(-72.3,-206.2),(-71.3,-206.2),(-70.75,-206.45),(-70.45,-207.0),(-70.0,-208.0),(-69.5,-209.0),(-69.0,-210.5),(-68.5,-211.5)]
def chaikin(p,n=2):
    for _ in range(n):
        q=[p[0]]
        for a,b in zip(p[:-1],p[1:]): q+= [(0.75*a[0]+0.25*b[0],0.75*a[1]+0.25*b[1]),(0.25*a[0]+0.75*b[0],0.25*a[1]+0.75*b[1])]
        q.append(p[-1]); p=q
    return p
NL=chaikin(P)
def nose_x(y):  # x of the curb line at y (for y <= -206.2), else None
    for a,b in zip(NL[:-1],NL[1:]):
        if min(a[1],b[1])-1e-9<=y<=max(a[1],b[1])+1e-9 and abs(a[1]-b[1])>1e-6:
            return a[0]+(b[0]-a[0])*(y-a[1])/(b[1]-a[1])
    return None
def asphalt_side(x,y):
    if y>-206.2: return x>=-72.3 or y>-205.5  # W of -72.3 below -205.5 = WS141 pad concrete
    nx=nose_x(y); return nx is not None and x>nx
col=bpy.data.collections.get('WS145_walk_nose') or bpy.data.collections.new('WS145_walk_nose')
if col.name not in bpy.context.scene.collection.children: bpy.context.scene.collection.children.link(col)
for o in [o for o in OB if o.name.startswith('WS145_')]: OB.remove(o)
asm=bpy.data.materials.get('WS27_CollegeAve_asphalt_2020ortho'); cm=bpy.data.materials.get('WS27_curb_concrete_UNVERIFIED')
# 1. trim WS136a walk faces whose centre is on the asphalt side within the nose window
walk=[o for o in OB if o.type=='MESH' and o.name.startswith('WS136a_Skyline')]
ndel=0
for o in walk:
    bm=bmesh.new(); bm.from_mesh(o.data); mw=o.matrix_world; k=[]
    for f in bm.faces:
        c=mw@f.calc_center_median()
        if XW-0.1<c.x<XE+0.3 and -211.6<c.y<YTOP+0.5 and asphalt_side(c.x,c.y): k.append(f)
    if k: bmesh.ops.delete(bm,geom=k,context='FACES'); bm.to_mesh(o.data); o.data.update(); print('TRIM',o.name,len(k)); ndel+=len(k)
    bm.free()
if not walk: print('MISSING WS136a walk')
# 2. asphalt fill (0.25 m cells) between YTOP and the nose line, skipping cells already covered by lot/Skyline Way asphalt
cov=[]
for nm in ('WS142_Lot9_asphalt','WS135a_Skyline_Way_asphalt','WS141_BK_NE_concrete_pad'):
    for o in [o for o in OB if o.type=='MESH' and o.name.startswith(nm)]:
        cov.append(BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[p.vertices for p in o.data.polygons]))
def covered(x,y): return any(t.ray_cast(Vector((x,y,300)),Vector((0,0,-1)))[0] is not None for t in cov)
S=0.25; bm=bmesh.new(); V={}
def v(i,j):
    if (i,j) not in V: x=XW+i*S; y=YTOP-j*S; V[(i,j)]=bm.verts.new((x,y,lz(x,y)))
    return V[(i,j)]
ni=int(round((XE-XW)/S)); nj=int(round((YTOP+211.5)/S)); nf=0
for i in range(ni):
    for j in range(nj):
        cx=XW+(i+0.5)*S; cy=YTOP-(j+0.5)*S
        if asphalt_side(cx,cy) and not covered(cx,cy):
            bm.faces.new((v(i,j+1),v(i+1,j+1),v(i+1,j),v(i,j))); nf+=1
for f in bm.faces:
    f.normal_update()
    if f.normal.z<0: f.normal_flip()
me=bpy.data.meshes.new('WS145_walk_nose_lot_asphalt_LiDAR2023int'); bm.to_mesh(me); bm.free()
if asm: me.materials.append(asm)
uvl=me.uv_layers.new(name='UVMap')
for lp in me.loops:
    p=me.vertices[lp.vertex_index].co; uvl.data[lp.index].uv=(p.x*0.25,p.y*0.25)
fill=OB.new(me.name,me); col.objects.link(fill); print('FILL faces',nf,'deleted',ndel)
# 3. nose curb (0.15 m wide on the walk side, reveal 0.10 above asphalt), walk-side normal = W/S of the line
bm=bmesh.new(); pts=[]
for a,b in zip(NL[:-1],NL[1:]):
    a=np.array(a); b=np.array(b); n=max(1,int(math.ceil(np.linalg.norm(b-a)/0.25)))
    for s in range(n): pts.append(a+(b-a)*s/n)
pts.append(np.array(NL[-1])); rings=[]
for k,p in enumerate(pts):
    q=pts[min(k+1,len(pts)-1)]-pts[max(k-1,0)]; d=q/np.linalg.norm(q); nrm=np.array([d[1],-d[0]])  # right of travel (E->S) = walk side
    z=lz(p[0],p[1]); b=p+nrm*0.15
    rings.append([bm.verts.new((p[0],p[1],z-0.30)),bm.verts.new((p[0],p[1],z+0.10)),bm.verts.new((b[0],b[1],z+0.10)),bm.verts.new((b[0],b[1],z-0.30))])
for i in range(len(rings)-1):
    for j in range(3): bm.faces.new((rings[i][j],rings[i+1][j],rings[i+1][j+1],rings[i][j+1]))
    bm.faces.new((rings[i][3],rings[i+1][3],rings[i+1][0],rings[i][0]))
bm.faces.new(rings[0][::-1]); bm.faces.new(rings[-1]); bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
cme=bpy.data.meshes.new('WS145_walk_N_nose_curb_LiDAR2023_UNVERIFIEDsection'); bm.to_mesh(cme); bm.free()
if cm: cme.materials.append(cm)
curb=OB.new(cme.name,cme); col.objects.link(curb)
cx=[c.co.x for c in cme.vertices]; cyy=[c.co.y for c in cme.vertices]
print('CURB x',round(min(cx),2),round(max(cx),2),'y',round(min(cyy),2),round(max(cyy),2))
# 4. push ground 10 cm under the fill + curb
T=BVHTree.FromPolygons([fill.matrix_world@v.co for v in fill.data.vertices]+[curb.matrix_world@v.co for v in cme.vertices],
    [p.vertices for p in fill.data.polygons]+[[i+len(fill.data.vertices) for i in p.vertices] for p in cme.polygons])
def ztop(x,y):
    h=T.ray_cast(Vector((x,y,300)),Vector((0,0,-1))); return h[0].z if h[0] is not None else None
nd=0
for g in [o for o in OB if o.type=='MESH' and o.name.startswith(('Terrain_LiDAR_DTM_1m','WS113_terrain_fan_fill','WS114_terrain_fan_fill','WS110_ground_patch','WS133b_','WS134_ground','WS60_terrain_edge_apron'))]:
    m=g.data; mw=np.array(g.matrix_world); n=len(m.vertices)
    co=np.empty(n*3); m.vertices.foreach_get('co',co); co=co.reshape(-1,3); Wc=co@mw[:3,:3].T+mw[:3,3]
    idx=np.nonzero((Wc[:,0]>XW-0.3)&(Wc[:,0]<XE+0.3)&(Wc[:,1]>-212)&(Wc[:,1]<YTOP+0.3))[0]; c=0
    for i in idx:
        zt=ztop(Wc[i,0],Wc[i,1])
        if zt is not None and Wc[i,2]>zt-0.10: Wc[i,2]=zt-0.10; c+=1
    if c:
        L=(Wc-mw[:3,3])@np.linalg.inv(mw[:3,:3]).T; m.vertices.foreach_set('co',L.ravel()); m.update(); nd+=c
print('ground pushed',nd)
px=OB.get('WS113_paving_tops_proxy')
if px:
    pbm=bmesh.new(); pbm.from_mesh(px.data); pmi=px.matrix_world.inverted()
    for p in fill.data.polygons: pbm.faces.new([pbm.verts.new(pmi@(fill.matrix_world@fill.data.vertices[i].co)) for i in p.vertices])
    pbm.to_mesh(px.data); pbm.free(); print('proxy +nose')
# 5. probes: fill edge vs lot (YTOP) and vs remaining walk top at the nose (walk should be ~curb reveal above asphalt)
for x in (-72.5,-71,-69.5):
    print('NOSENB lot',x,ztop(x,YTOP-0.1),'fill/lot top at',YTOP+0.1)
for o in walk:
    tr=BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[p.vertices for p in o.data.polygons])
    for (x,y) in ((-71.8,-206.6),(-71.0,-207.5),(-70.3,-209.0)):
        h=tr.ray_cast(Vector((x,y,300)),Vector((0,0,-1))); print('NOSENB walk',x,y,round(h[0].z,3) if h[0] else None,'asphalt',round(lz(x,y),3))
if OUT: bpy.ops.wm.save_as_mainfile(filepath=OUT,copy=True); print('SAVED',OUT)
