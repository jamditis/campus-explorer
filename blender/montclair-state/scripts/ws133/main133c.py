# ws133c: the grey smear S/E of Russ is WS60_terrain_edge_apron_LiDAR_to_skirt (LiDAR terrain stops here; the apron runs
# ~1.7-2 m BELOW the 2023 ground down to the skirt). Rebuild WS133b as a 1 x 0.5 m 2023-DTM patch over x -172..-112,
# y -280..-249.5 (minus the Russ footprint): lawn within 5 m of Russ/the E walk, the 2020-ortho drape elsewhere (same 'ortho'
# corner mapping as WS113 fill) so the unbuilt drive/lot S of Russ and the dining-link area keep their ortho evidence at true height.
import bpy, bmesh, math, os, numpy as np
from mathutils import Vector
SAVE=os.environ.get('SAVE','0')=='1'
D='/workspace/nj-scenes/montclair-state/scripts/'
P=np.load(D+'ws132/las132.npy'); G2=P[P[:,3]==2]
c=math.hypot(1,0.24); U=np.array([1,-0.24])/c; V=np.array([0.24,1])/c; O=np.array([-150.,-242.])
def ST(x,y): d=np.array([x,y])-O; return float(d@U),float(d@V)
def gzxy(x,y,r=1.5):
    d2=(G2[:,0]-x)**2+(G2[:,1]-y)**2; m=d2<r*r
    if m.sum()<4: m=d2<(3*r)**2
    if m.sum()<1: m=d2<100
    w=1/(0.3+d2[m]); return float((G2[m,2]*w).sum()/w.sum())
R=[(-17,19,-7.25,7.3),(-23.8,-10.3,-11.55,11.8),(12,24.95,-11.65,11.75),(-31,-23,-6.1,6.6),(-23,-11.5,-14.5,-11),(13,24.1,-14.6,-11)]
def dist_b(x,y):
    s,t=ST(x,y); best=1e9
    for r in R+[(24.95,34.6,-15.5,13.0)]:
        ds=max(r[0]-s,0,s-r[1]); dt=max(r[2]-t,0,t-r[3]); best=min(best,math.hypot(ds,dt))
    return best
def inb(x,y):
    s,t=ST(x,y); return any(r[0]-0.3<=s<=r[1]+0.3 and r[2]-0.3<=t<=r[3]+0.3 for r in R)
col=bpy.data.collections['WS133_Russ_E_side']
for o in [o for o in bpy.data.objects if o.name.startswith('WS133b_')]: bpy.data.objects.remove(o)
# fit WS113 'ortho' corner mapping
f=bpy.data.objects['WS113_terrain_fan_fill_DTM1m_UNVERIFIEDgrade']; fm=f.data; at=fm.attributes['ortho']
print('ATTR',at.data_type,at.domain)
xs=[];us=[]
for k,lp in enumerate(fm.loops[:4000]):
    p=f.matrix_world@fm.vertices[lp.vertex_index].co; xs.append((p.x,p.y,1)); us.append(tuple(at.data[k].vector)[:2])
A=np.array(xs); Uv=np.array(us); coef,_,_,_=np.linalg.lstsq(A,Uv,rcond=None); print('COEF',coef.round(6).tolist())
X=np.arange(-172,-112+1e-6,1.0); Y=np.arange(-280,-249.5+1e-6,0.5)
bm=bmesh.new(); vid={}
def v(i,j):
    if (i,j) not in vid: vid[(i,j)]=bm.verts.new((float(X[i]),float(Y[j]),gzxy(X[i],Y[j])-0.01))
    return vid[(i,j)]
mats=[]
for i in range(len(X)-1):
    for j in range(len(Y)-1):
        cx,cy=(X[i]+X[i+1])/2,(Y[j]+Y[j+1])/2
        if inb(cx,cy): continue
        fc=bm.faces.new((v(i,j),v(i+1,j),v(i+1,j+1),v(i,j+1)))
        fc.material_index=0 if dist_b(cx,cy)<5.0 and cx>-150 else 1
me=bpy.data.meshes.new('WS133b_ground_patch_Russ_S_E_DTM2023_lawn5m_else_ortho2020_UNVERIFIED'); bm.to_mesh(me); bm.free()
me.materials.append(bpy.data.materials['COLE_lawn_post2020_bs']); me.materials.append(fm.materials[0])
na=me.attributes.new('ortho',at.data_type,at.domain)
for k,lp in enumerate(me.loops):
    p=me.vertices[lp.vertex_index].co; uv=np.array([p.x,p.y,1])@coef
    if at.data_type=='FLOAT2': na.data[k].vector=(float(uv[0]),float(uv[1]))
    else: na.data[k].vector=(float(uv[0]),float(uv[1]),0.0)
o=bpy.data.objects.new(me.name,me); col.objects.link(o)
print('PATCH faces',len(me.polygons),'lawn',sum(1 for p in me.polygons if p.material_index==0))
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
