# ws247 W62e: walk along the back (east side) of the soccer field's east stand, traced from the 2020 NJ ortho (crop247/247b:
# a ~3 m pale concrete strip from the plaza S of the stand (y 52) north to the OSM path at the University Hall plaza (y 154);
# not in OSM). Pass 1: drape the strip on the EVALUATED terrain (GN on) and write verts/faces to h247.json.
import bpy, os, json, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
F='/workspace/nj-scenes/montclair-state/'+os.environ.get('F','montclair_state_ws247a.blend')
with bpy.data.libraries.load(F) as (a,b): b.objects=['Terrain_LiDAR_DTM_1m','fse_stand_under_pad','Footpaths_OSM']
for o in b.objects: bpy.context.scene.collection.objects.link(o)
T,PAD,FP=b.objects
for m in T.modifiers:
    if 'skirt_under' in m.name.lower(): m.show_viewport=False
bpy.context.view_layer.update(); dg=bpy.context.evaluated_depsgraph_get()
def bvh(o,box=(-245,-200,40,165)):
    e=o.evaluated_get(dg); me=e.to_mesh(); M=o.matrix_world; vs=[M@v.co for v in me.vertices]
    ps=[p.vertices[:] for p in me.polygons if any(box[0]<vs[i].x<box[1] and box[2]<vs[i].y<box[3] for i in p.vertices)]
    t=BVHTree.FromPolygons(vs,ps); e.to_mesh_clear(); return t
TB=bvh(T); PB=bvh(PAD); FB=bvh(FP)
def z(t,x,y):
    h=t.ray_cast(Vector((x,y,300)),Vector((0,0,-1)),400); return None if h[0] is None else h[0].z
# ortho trace (centre of the pale run, 0.25 m texels), y -> x
TR=[(52,-232.2),(54,-231.6),(57,-230.75),(60,-230.0),(63,-229.5),(66,-228.75),(69,-228.1),(72,-227.4),(75,-226.75),(78,-226.1),(81,-225.25),(84,-224.75),(86,-224.5),(89,-224.1),(92,-223.1),(95,-222.4),(98,-221.75),(101,-221.25),(104,-220.25),(107,-219.75),(110,-219.1),(113,-218.4),(116,-217.75),(119,-217.1),(122,-216.6),(125,-216.0),(128,-215.75),(131,-215.75),(134,-215.75),(137,-215.75),(140,-215.75),(143,-215.85),(146,-215.85),(149,-215.85),(152,-215.85),(154,-215.4)]
ty=np.array([p[0] for p in TR],float); tx=np.array([p[1] for p in TR],float)
k=np.ones(5)/5; txs=np.convolve(np.pad(tx,2,mode='edge'),k,'valid')   # 5-pt smoothing (texel noise)
W=float(os.environ.get('W247','2.8')); ys=np.arange(52,154.01,0.5); cx=np.interp(ys,ty,txs)
def padE(y):  # east edge of the stand pad at y (ray scan west from x -200)
    for x in np.arange(-212,-246,-0.1):
        if PB.ray_cast(Vector((x,y,300)),Vector((0,0,-1)),400)[0] is not None: return x
    return None
V=[];Fc=[];nv=0;rows=[];moved=0;lo=[]
ACR=[-0.5,-1/6,1/6,0.5]
for i,y in enumerate(ys):
    # direction along path
    j0=max(i-1,0); j1=min(i+1,len(ys)-1); d=np.array([cx[j1]-cx[j0],ys[j1]-ys[j0]]); d/=np.linalg.norm(d); n=np.array([d[1],-d[0]])  # n points east
    c=np.array([cx[i],y]); pe=padE(y)
    if pe is not None and (c-n*W/2)[0]<pe+0.05: c=c+n*((pe+0.05)-(c-n*W/2)[0])/n[0]; moved+=1
    r=[]
    for a in ACR:
        p=c+n*W*a; zz=z(TB,p[0],p[1])
        zp=z(PB,p[0],p[1]); zf=z(FB,p[0],p[1])
        if zz is None: zz=zf if zf is not None else 134.4
        if zf is not None: zz=max(zz,zf)
        r.append([p[0],p[1],zz+0.04])
    g=[q[2] for q in r]; lo.append(min(g)-0.04)
    if os.environ.get('LEVEL','1')=='1':
        for q in r: q[2]=max(g)
    rows.append(r)
R=np.array(rows)  # n x 4 x 3
# light along-path smoothing of z (0.5 m step, 3-pt), never below terrain+0.03
Zt=R[:,:,2].copy()
for it in range(2):
    Zs=Zt.copy(); Zs[1:-1]=(Zt[:-2]+Zt[1:-1]+Zt[2:])/3; Zt=np.maximum(Zs,R[:,:,2]-0.01)
R[:,:,2]=Zt
LO=np.array(lo); _k=0
for r in R:
    for p in r: V.append(tuple(map(float,p)))
    # skirts 0.15 m down at both edges
    V.append((float(r[0][0]),float(r[0][1]),float(min(r[0][2]-0.15,LO[_k]-0.05)))); V.append((float(r[-1][0]),float(r[-1][1]),float(min(r[-1][2]-0.15,LO[_k]-0.05)))); _k+=1
S=6
for i in range(len(R)-1):
    a=i*S; b=(i+1)*S
    for q in range(3): Fc.append((a+q,a+q+1,b+q+1,b+q))
    Fc.append((a+4,a,b,b+4)); Fc.append((a+3,a+5,b+5,b+3))
cr=R[:,:,:2].reshape(-1,2)
print('H247 max skirt drop',round(float((R[:,:,2].max(1)-LO).max()),2),'rows with drop>0.3',int(((R[:,:,2].max(1)-LO)>0.3).sum()));print('H247 rows',len(R),'verts',len(V),'faces',len(Fc),'shifted off pad',moved,'z range',round(R[:,:,2].min(),2),round(R[:,:,2].max(),2),'max cross-slope m/m',round(float(np.max(np.abs(R[:,-1,2]-R[:,0,2]))/W),2),flush=True)
for y in (52,60,80,100,120,140,154):
    i=int((y-52)/0.5) if y<154 else len(R)-1; print('H247 y',y,'x',round(R[i,0,0],2),round(R[i,-1,0],2),'z',round(R[i,0,2],2),round(R[i,-1,2],2),'pad',padE(y),flush=True)
json.dump({'V':V,'F':Fc},open('/workspace/nj-scenes/montclair-state/scripts/ws247/h247.json','w'))
os._exit(0)
