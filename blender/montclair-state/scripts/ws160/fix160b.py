# ws160b on ws160a: evergreen bed N of the Panzer N wing (2020 ortho shows a dark evergreen mass between the gym E wall and the walk/spur, a 26.6-34, b -8.8..-0.15), LiDAR-draped mulch + yew masses (species UNVERIFIED)
import bpy, bmesh, math, numpy as np, random
from mathutils import Vector
M='/workspace/nj-scenes/montclair-state/'
th=math.radians(76.8); A=Vector((math.cos(th),math.sin(th),0)); B=Vector((math.cos(th-math.pi/2),math.sin(th-math.pi/2),0)); O=Vector((-238.1,-180.2,0))
def P(a,b,z): return O+A*a+B*b+Vector((0,0,z))
d=np.load(M+'data/pts_panzer158.npz'); X,Y,Z,C=d['x'],d['y'],d['z'],d['c']
g=C==2; X,Y,Z=X[g],Y[g],Z[g]; ga=(X-O.x)*A.x+(Y-O.y)*A.y; gb=(X-O.x)*B.x+(Y-O.y)*B.y
def gz(a,b,r=0.8):
    m=(abs(ga-a)<r)&(abs(gb-b)<r)
    if m.sum()<3: m=(abs(ga-a)<1.6)&(abs(gb-b)<1.6)
    return float(np.median(Z[m])) if m.sum()>=3 else 122.4
col=bpy.data.collections['WS159_Panzer_front_walk_beds']
MUL=bpy.data.materials['WS159_mulch_dark_shredded']
av=np.arange(26.6,34.01,0.5); bv=np.arange(-8.8,-0.149,0.5)
H=np.array([[gz(a,b) for b in bv] for a in av])
from numpy.lib.stride_tricks import sliding_window_view
H=sliding_window_view(np.pad(H,1,mode='edge'),(3,3)).mean(axis=(2,3))
# walk-side edge sits 2 cm above the regraded walk ext (122.31+0.0357(a-25))
for i,a in enumerate(av): H[i,-1]=max(H[i,-1],122.31+0.0357*(a-25)-0.03)
V=[];F=[];idx={}
for i,a in enumerate(av):
    for j,b in enumerate(bv): idx[i,j]=len(V); V.append(P(a,b,H[i,j]+0.05))
for i in range(len(av)-1):
    for j in range(len(bv)-1): F.append([idx[i,j],idx[i+1,j],idx[i+1,j+1],idx[i,j+1]])
me=bpy.data.meshes.new('WS160b_PanzerE_N_evergreen_bed_mulch_ortho2020_LiDAR'); me.from_pydata([tuple(v) for v in V],[],F); me.materials.append(MUL)
o=bpy.data.objects.new(me.name,me); col.objects.link(o)
print('FIX160B bed z',round(float(H.min()),2),round(float(H.max()),2))
src=[ob for ob in bpy.data.objects if ob.name.startswith('WS105_bank_shrub_') and ob.data.materials and 'Yew' in ob.data.materials[0].name]
print('FIX160B yew src',[s.name for s in src][:4], [tuple(round(x,2) for x in s.dimensions) for s in src][:2], [tuple(round(x,2) for x in s.location) for s in src][:2])
random.seed(160); n=0
spots=[(28.0,-7.4),(30.3,-7.6),(32.6,-7.3),(27.6,-5.0),(29.6,-4.9),(31.8,-5.2),(33.6,-4.6),(28.6,-2.6),(30.8,-2.5),(32.9,-2.2)]
for a,b in spots:
    s=random.choice(src); c=s.copy(); c.name='WS160b_PanzerE_N_bed_yew_%02d_ortho2020_UNVERIFIED'%n; col.objects.link(c)
    c.location=P(a,b,gz(a,b)+0.03); k=random.uniform(1.25,1.7); c.scale=(s.scale[0]*k,s.scale[1]*k,s.scale[2]*k*random.uniform(0.9,1.1)); c.rotation_euler[2]=random.uniform(0,6.28); n+=1
print('FIX160B yews',n)
bpy.ops.wm.save_as_mainfile(filepath=M+'montclair_state_ws160b.blend',compress=True)
print('FIX160B SAVED')
