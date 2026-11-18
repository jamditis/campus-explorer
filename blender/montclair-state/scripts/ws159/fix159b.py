# ws159b: extend the Panzer front clean-up N of the N wing (a 24..34), walk to a 32 on LiDAR, sloped step cheek walls
import bpy, bmesh, math, numpy as np
from mathutils import Vector
M='/workspace/nj-scenes/montclair-state/'
th=math.radians(76.8); A=Vector((math.cos(th),math.sin(th),0)); B=Vector((math.cos(th-math.pi/2),math.sin(th-math.pi/2),0)); O=Vector((-238.1,-180.2,0))
def P(a,b,z): return O+A*a+B*b+Vector((0,0,z))
def AB(v): w=Vector((v.x,v.y,0))-O; return w.dot(A), w.dot(B)
d=np.load(M+'data/pts_panzer158.npz'); X,Y,Z,C=d['x'],d['y'],d['z'],d['c']
g=C==2; X,Y,Z=X[g],Y[g],Z[g]; ga=(X-O.x)*A.x+(Y-O.y)*A.y; gb=(X-O.x)*B.x+(Y-O.y)*B.y
def gz(a,b,r=0.8):
    m=(abs(ga-a)<r)&(abs(gb-b)<r); return float(np.median(Z[m])) if m.sum()>=3 else None
Z2=(24.0,34.0,-3.0,4.5)
# report what sits in the zone
for ob in bpy.data.objects:
    if ob.type!='MESH' or ob.name.startswith(('WS158','WS159')) or ob.hide_render: continue
    bb=[ob.matrix_world@Vector(c) for c in ob.bound_box]; abv=[AB(v) for v in bb]
    if max(a for a,b in abv)<Z2[0] or min(a for a,b in abv)>Z2[1] or max(b for a,b in abv)<Z2[2] or min(b for a,b in abv)>Z2[3]: continue
    if len(ob.data.polygons)>400000: print('FIX159B big skip',ob.name); continue
    mw=ob.matrix_world; cnt=0; zs=[]
    for p in ob.data.polygons:
        c=mw@p.center; a,b=AB(c)
        if Z2[0]<=a<=Z2[1] and Z2[2]<=b<=Z2[3]: cnt+=1; zs.append(c.z)
    if cnt: print('FIX159B in-zone',ob.name,cnt,round(min(zs),2),round(max(zs),2),[m.type for m in ob.modifiers])
tot=0
for ob in list(bpy.data.objects):
    if ob.type!='MESH': continue
    n=ob.name
    if not (n=='Footpaths_OSM' or n.startswith('WS86_grandstand_DTM_target') or n.startswith('OZ_walk_joints')): continue
    mw=ob.matrix_world; me=ob.data
    cand=[p.index for p in me.polygons if (lambda ab_: Z2[0]<=ab_[0]<=Z2[1] and Z2[2]<=ab_[1]<=Z2[3])(AB(mw@p.center))]
    if not cand: continue
    if me.users>1: ob.data=me.copy(); me=ob.data
    bm=bmesh.new(); bm.from_mesh(me); bm.faces.ensure_lookup_table(); bmesh.ops.delete(bm,geom=[bm.faces[i] for i in cand],context='FACES'); bm.to_mesh(me); bm.free(); tot+=len(cand)
    print('FIX159B clip',n,len(cand))
col=bpy.data.collections['WS159_Panzer_front_walk_beds']
CON=bpy.data.materials['WS159_concrete_walk_broomed']; EDG=bpy.data.materials['WS159_bed_edge_concrete_curb']
# walk extension a 25..32 on LiDAR (rises ~122.31 -> 122.5), b 0..3.2, 0.5 m strips
ZW=122.31; V=[];F=[]; av=list(np.arange(25.0,32.01,0.5))
zz=[]
for a in av:
    z=gz(a,1.6); zz.append(max(ZW, z if z is not None else ZW))
zz=np.maximum.accumulate(np.convolve(np.pad(zz,2,mode='edge'),np.ones(5)/5,mode='valid')); zz[0]=ZW
for i,a in enumerate(av):
    for b in (0.0,3.2):
        V.append(P(a,b,zz[i]+0.0))
    for b in (0.0,3.2): V.append(P(a,b,zz[i]-0.15))
for i in range(len(av)-1):
    k=4*i; n=4*(i+1); F+= [[k,n,n+1,k+1],[k+2,k+3,n+3,n+2],[k,k+2,n+2,n],[k+1,n+1,n+3,k+3]]
k=4*(len(av)-1); F.append([k,k+1,k+3,k+2])
me=bpy.data.meshes.new('WS159b_PanzerE_front_walk_ext_N_LiDAR'); me.from_pydata([tuple(v) for v in V],[],F); me.materials.append(CON)
bm=bmesh.new(); bm.from_mesh(me); bmesh.ops.recalc_face_normals(bm,faces=bm.faces); bm.to_mesh(me); bm.free()
o=bpy.data.objects.new(me.name,me); col.objects.link(o)
print('FIX159B walk ext z',round(float(zz[0]),2),round(float(zz[-1]),2))
# sloped cheek walls replace the flat-topped boxes
old=bpy.data.objects.get('WS159_PanzerE_step_cheek_walls')
if old: bpy.data.objects.remove(old)
st=bpy.data.objects['WS159_PanzerE_bank_steps_concrete_OSM312847984']; ztop=max((st.matrix_world@v.co).z for v in st.data.vertices)
V=[];F=[]
for a0,a1 in ((8.3,8.5),(10.9,11.1)):
    o_=len(V); b0,b1=3.2,8.5; zt0,zt1=ZW+0.35,ztop+0.15
    for (a,b,z) in [(a0,b0,ZW-0.2),(a1,b0,ZW-0.2),(a1,b1,ZW-0.2),(a0,b1,ZW-0.2),(a0,b0,zt0),(a1,b0,zt0),(a1,b1,zt1),(a0,b1,zt1)]: V.append(P(a,b,z))
    F+=[[o_+q for q in f] for f in [[0,1,2,3],[7,6,5,4],[0,4,5,1],[1,5,6,2],[2,6,7,3],[3,7,4,0]]]
me=bpy.data.meshes.new('WS159b_PanzerE_step_cheek_walls_sloped'); me.from_pydata([tuple(v) for v in V],[],F); me.materials.append(EDG)
bm=bmesh.new(); bm.from_mesh(me); bmesh.ops.recalc_face_normals(bm,faces=bm.faces); bm.to_mesh(me); bm.free()
o=bpy.data.objects.new(me.name,me); col.objects.link(o)
bpy.ops.wm.save_as_mainfile(filepath=M+'montclair_state_ws159b.blend',compress=False)
print('FIX159B SAVED',tot)
