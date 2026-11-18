# ws143: forecourt tree pit + small tree. LiDAR class-1 crown 4.8 x 4.5 m, max 4.3 m over ground, centroid (-75.4,-172.3);
# ground intensity 1.8-3.5k in a ~1.6 m spot at (-75.8,-171.9) inside the 11-13k concrete = tree pit (mulch/soil). Species UNVERIFIED.
import bpy, bmesh, math
from mathutils import Vector, Matrix
TX,TY,TH,CW=-75.8,-171.9,4.3,4.6
mul=bpy.data.materials.get('WS3_Mulch_bark_dark_brown')
bm=bmesh.new(); c=bm.verts.new((TX,TY,lz(TX,TY)+0.045)); ring=[]
for k in range(24):
    a=2*math.pi*k/24; x=TX+0.8*math.cos(a); y=TY+0.8*math.sin(a); ring.append(bm.verts.new((x,y,lz(x,y)+0.045)))
for k in range(24): bm.faces.new((c,ring[k],ring[(k+1)%24]))
me=bpy.data.meshes.new('WS143_forecourt_tree_pit_mulch_LiDAR2023int_UNVERIFIED'); bm.to_mesh(me); bm.free()
if mul: me.materials.append(mul)
col.objects.link(OB.new(me.name,me))
s=OB.get('T_RedMaple_L1_0004')
if s:
    bb=[s.matrix_world@Vector(q) for q in s.bound_box]
    sh=max(q.z for q in bb)-min(q.z for q in bb); sw=max(max(q.x for q in bb)-min(q.x for q in bb),max(q.y for q in bb)-min(q.y for q in bb))
    k=TH/sh; kx=min(1.6,max(1.0,CW/(sw*k)))
    cx=sum(q.x for q in bb)/8; cy=sum(q.y for q in bb)/8; mz=min(q.z for q in bb)
    t=s.copy(); t.name='WS143_forecourt_tree_small_ornamental_LiDAR2023_h4m_UNVERIFIEDspecies'
    for cc in t.users_collection: cc.objects.unlink(t)
    col.objects.link(t)
    t.scale=Vector((s.scale.x*k*kx,s.scale.y*k*kx,s.scale.z*k))
    off=Vector(((cx-s.location.x)*k*kx,(cy-s.location.y)*k*kx,(mz-s.location.z)*k))
    t.location=Vector((TX,TY,lz(TX,TY)-0.10))-off
    print('TREE143',round(k,3),round(kx,2),tuple(round(a,2) for a in t.location))
else: print('TREE143 source missing')
