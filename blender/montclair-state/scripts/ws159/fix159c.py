# ws159c: OSM footway 312847991 spur N of the N wing (a 25.4 b 1.8 -> 25.2,-3.3 -> 25.7,-6.1 -> 27.1,-6.8), LiDAR flat ~122.2-122.3; compressed save
import bpy, bmesh, math
from mathutils import Vector
M='/workspace/nj-scenes/montclair-state/'
th=math.radians(76.8); A=Vector((math.cos(th),math.sin(th),0)); B=Vector((math.cos(th-math.pi/2),math.sin(th-math.pi/2),0)); O=Vector((-238.1,-180.2,0))
def P(a,b,z): return O+A*a+B*b+Vector((0,0,z))
def AB(v): w=Vector((v.x,v.y,0))-O; return w.dot(A), w.dot(B)
# clip old draped footpath faces in the spur zone
Z3=(24.0,29.0,-8.0,0.0); tot=0
for n in ('Footpaths_OSM','WS86_grandstand_DTM_target'):
    ob=bpy.data.objects.get(n)
    if not ob: continue
    mw=ob.matrix_world; me=ob.data
    cand=[p.index for p in me.polygons if (lambda q: Z3[0]<=q[0]<=Z3[1] and Z3[2]<=q[1]<=Z3[3])(AB(mw@p.center))]
    if cand:
        bm=bmesh.new(); bm.from_mesh(me); bm.faces.ensure_lookup_table(); bmesh.ops.delete(bm,geom=[bm.faces[i] for i in cand],context='FACES'); bm.to_mesh(me); bm.free(); tot+=len(cand)
print('FIX159C clipped',tot)
pts=[(25.4,0.2),(25.3,-1.5),(25.2,-3.3),(25.7,-6.1),(27.1,-6.8)]; W=1.0; ZT=122.30
V=[];F=[]
for i,(a,b) in enumerate(pts):
    if i==0: t=Vector((pts[1][0]-a,pts[1][1]-b,0))
    elif i==len(pts)-1: t=Vector((a-pts[i-1][0],b-pts[i-1][1],0))
    else: t=Vector((pts[i+1][0]-pts[i-1][0],pts[i+1][1]-pts[i-1][1],0))
    t.normalize(); nrm=Vector((-t.y,t.x,0))
    for s in (-W,W):
        V.append(P(a+nrm.x*s,b+nrm.y*s,ZT))
    for s in (-W,W):
        V.append(P(a+nrm.x*s,b+nrm.y*s,ZT-0.15))
for i in range(len(pts)-1):
    k=4*i; n=k+4; F+=[[k,n,n+1,k+1],[k+2,k+3,n+3,n+2],[k,k+2,n+2,n],[k+1,n+1,n+3,k+3]]
k=4*(len(pts)-1); F.append([k,k+1,k+3,k+2])
me=bpy.data.meshes.new('WS159c_PanzerE_N_spur_walk_OSM312847991'); me.from_pydata([tuple(v) for v in V],[],F); me.materials.append(bpy.data.materials['WS159_concrete_walk_broomed'])
bm=bmesh.new(); bm.from_mesh(me); bmesh.ops.recalc_face_normals(bm,faces=bm.faces); bm.to_mesh(me); bm.free()
o=bpy.data.objects.new(me.name,me); bpy.data.collections['WS159_Panzer_front_walk_beds'].objects.link(o)
bpy.ops.wm.save_as_mainfile(filepath=M+'montclair_state_ws159c.blend',compress=True)
print('FIX159C SAVED')
