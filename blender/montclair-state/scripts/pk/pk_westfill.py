# pk: the LiDAR DTM in MAIN stops at x≈-246 (straight cut), so the west part of Feliciano (x -258..-246) stood over the 4 km
# 3DEP context skirt 1.1-1.8 m below its wall bottoms -> black band at grade in the N/W views. Adds
# PK_Feliciano_west_DTM_fill_UNVERIFIED: a 1 m terrain sheet from north/data/grid_1m.npz 'dtm_filled' (same 2023/2017 LiDAR
# ground as the north scene), offset per row to meet the MAIN DTM edge (3 cm under it in a 0.6 m overlap), feathered to the
# skirt height over the last 15 m in the west. Same Ground_ortho_grass material + 'ortho' UV fitted from the DTM. REVERT=1 deletes.
import bpy,bmesh,os,sys,math,time
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
t0=time.time(); ON='PK_Feliciano_west_DTM_fill_UNVERIFIED'
if ON in bpy.data.objects:
    o=bpy.data.objects[ON]; m=o.data; bpy.data.objects.remove(o); bpy.data.meshes.remove(m)
if os.environ.get('REVERT')=='1':
    if '--save' in sys.argv: bpy.ops.wm.save_mainfile()
    print('PKW_REVERTED',len(bpy.data.objects)); raise SystemExit(0)
G=np.load('/workspace/nj-scenes/montclair-state/north/data/grid_1m.npz'); D=G['dtm_filled']; GX0,GY0=-600.0,-260.0
def g(x,y):  # bilinear, cell centres at GX0+c+0.5 (rows bottom-up)
    fx=x-GX0-0.5; fy=y-GY0-0.5; c=int(math.floor(fx)); r=int(math.floor(fy)); tx=fx-c; ty=fy-r
    return float(D[r,c]*(1-tx)*(1-ty)+D[r,c+1]*tx*(1-ty)+D[r+1,c]*(1-tx)*ty+D[r+1,c+1]*tx*ty)
XW,YS,YN=-320.0,106.0,274.0; FW=25.0; FNS=20.0
T=bpy.data.objects['Terrain_LiDAR_DTM_1m']; tm=T.matrix_world; me=T.data
tv=[tm@v.co for v in me.vertices]
ins=[-330<=v.x<=-200 and 90<=v.y<=290 for v in tv]
polys=[p for p in me.polygons if any(ins[i] for i in p.vertices)]
used=sorted({i for p in polys for i in p.vertices}); rm={o:n for n,o in enumerate(used)}
bt=BVHTree.FromPolygons([tv[i] for i in used],[[rm[i] for i in p.vertices] for p in polys])
S=bpy.data.objects['Context_skirt_3DEP_ortho_4km']; sm=S.matrix_world; sv=[sm@v.co for v in S.data.vertices]
sins=[-340<=v.x<=-200 and 90<=v.y<=290 for v in sv]
sp=[list(p.vertices) for p in S.data.polygons if any(sins[i] for i in p.vertices)]
su=sorted({i for p in sp for i in p}); srm={o:n for n,o in enumerate(su)}
bs=BVHTree.FromPolygons([sv[i] for i in su],[[srm[i] for i in p] for p in sp])
DN=Vector((0,0,-1))
def tz(x,y):
    h=bt.ray_cast(Vector((x,y,400)),DN,600); return h[0].z if h[0] is not None else None
def szf(x,y):
    h=bs.ray_cast(Vector((x,y,400)),DN,600); return h[0].z if h[0] is not None else None
# ortho UV fit (least squares on loops of nearby DTM faces)
uv=me.uv_layers['ortho'].data; A=[];U=[];V=[]
import collections; mic=collections.Counter()
for p in polys[:4000]:
    for li in p.loop_indices:
        w=tv[me.loops[li].vertex_index]; A.append([w.x,w.y,1]); U.append(uv[li].uv[0]); V.append(uv[li].uv[1])
for p in polys:
    c=tm@p.center
    if c.x<-238: mic[p.material_index]+=1
A=np.array(A); cu=np.linalg.lstsq(A,np.array(U),rcond=None); cv=np.linalg.lstsq(A,np.array(V),rcond=None)
print('PKW uvfit res',cu[1],cv[1],'west mat idx',mic.most_common(3))
cu=cu[0]; cv=cv[0]
# per-row DTM edge
edge={}
for k in range(int(YS),int(YN)+1):
    x=-262.0
    while x<-200 and tz(x,k) is None: x+=0.1
    edge[k]=x if x<-200 else None
off={}
for k,ex in edge.items():
    if ex is None: continue
    z=tz(ex+0.3,k); off[k]=(z-g(ex+0.3,k)) if z is not None else 0.0
ks=sorted(off); print('PKW edge',[(k,round(edge[k],2),round(off[k],2)) for k in ks[::14]])
def offy(y):
    k=min(ks,key=lambda q:abs(q-y)); return off[k],edge[k]
bm=bmesh.new(); grid={}; nabove=0
ys=np.arange(YS,YN+0.01,1.0)
for j,y in enumerate(ys):
    o,ex=offy(y)
    xe=ex+0.6
    xs=list(np.arange(XW,xe,1.0))+[xe]
    for i,x in enumerate(xs): pass
    grid[j]=[]
    for x in xs:
        z=g(x,y)+o*max(0.0,1-(xe-x)/30.0)
        if x>ex-0.05: z-=0.03
        w=min(1.0,(x-XW)/FW,(y-YS)/FNS,(YN-y)/FNS)
        if w<1.0:
            s_=szf(x,y)
            if s_ is not None: z=s_-0.05+(z-(s_-0.05))*max(0.0,w)
        s_=szf(x,y)
        if s_ is not None and s_>z: nabove+=1
        grid[j].append(bm.verts.new((x,y,z)))
# faces: rows can differ in length by the edge; connect min length + fan the rest
for j in range(len(ys)-1):
    a=grid[j]; b=grid[j+1]; n=min(len(a),len(b))
    for i in range(n-1):
        bm.faces.new((a[i],a[i+1],b[i+1],b[i]))
    if len(a)>n:
        for i in range(n-1,len(a)-1): bm.faces.new((a[i],a[i+1],b[n-1]))
    elif len(b)>n:
        for i in range(n-1,len(b)-1): bm.faces.new((a[n-1],b[i+1],b[i]))
for f in bm.faces:
    if f.normal.z<0: f.normal_flip()
L=bm.loops.layers.uv.new('ortho')
for f in bm.faces:
    f.smooth=True
    for l in f.loops:
        co=l.vert.co; l[L].uv=(cu[0]*co.x+cu[1]*co.y+cu[2], cv[0]*co.x+cv[1]*co.y+cv[2])
nm=bpy.data.meshes.new(ON); bm.to_mesh(nm); bm.free()
mi=mic.most_common(1)[0][0] if mic else 0
nm.materials.append(T.material_slots[mi].material)
o=bpy.data.objects.new(ON,nm); T.users_collection[0].objects.link(o)
o['UNVERIFIED']='terrain west of the MAIN LiDAR DTM cut at x~-246 near Feliciano, from north grid_1m dtm_filled (interpolated under buildings), offset to the DTM edge'
print('PKW verts',len(nm.vertices),'faces',len(nm.polygons),'skirt above fill',nabove,'mat',nm.materials[0].name,'t',round(time.time()-t0,1))
if '--save' in sys.argv: bpy.ops.wm.save_mainfile()
print('PKW_DONE',len(bpy.data.objects))
