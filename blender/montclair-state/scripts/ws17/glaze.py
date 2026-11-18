"""ws17: Cole north addition EAST face -> tall glazed section per Joe's aerial A (4 double-height bays
with piers, vertical mullions, one transom at the floor line), replacing the 2 rows of punched windows.
All UNVERIFIED best judgment from a distorted Google 3D view. SAVE=1 saves."""
import bpy, bmesh, os
from mathutils import Vector
o=bpy.data.objects['TZ_Cole_north_addition_UNVERIFIED']; me=o.data
slots=[s.material.name for s in o.material_slots]
STU=slots.index('TW_Cole_stucco_cream_UNVERIFIED'); MUL=slots.index('TZ_Cole_add_mullion_UNVERIFIED')
GLA=slots.index('TZ_Cole_add_glass_UNVERIFIED'); SILL=slots.index('TZ_Cole_sill_drip_UNVERIFIED')
bm=bmesh.new(); bm.from_mesh(me); bm.faces.ensure_lookup_table()
ref=bm.faces[434]; Fn=Vector((ref.normal.x,ref.normal.y,0)).normalized(); P=ref.verts[0].co.copy(); P.z=0
W=Vector((-Fn.y,Fn.x,0))
d=lambda co:(co-P).dot(Fn); u=lambda co:(co-P).dot(W)
wall=[f for f in bm.faces if f.material_index==STU and abs(f.normal.z)<0.1 and f.normal.dot(Fn)>0.99 and all(abs(d(v.co))<0.02 for v in f.verts)]
us=[u(v.co) for f in wall for v in f.verts]; zs=[v.co.z for f in wall for v in f.verts]
U0,U1,Z0,Z1=min(us),max(us),min(zs),max(zs)
print('EAST WALL faces',len(wall),'u',round(U0,3),round(U1,3),'L',round(U1-U0,2),'z',round(Z0,3),round(Z1,3))
kill=[f for f in bm.faces if all(-0.8<d(v.co)<0.2 and U0-0.01<u(v.co)<U1+0.01 and Z0-0.1<v.co.z<Z1+0.005 for v in f.verts)]
import collections; print('KILL',len(kill),collections.Counter(f.material_index for f in kill))
bmesh.ops.delete(bm,geom=kill,context='FACES')
L=U1-U0
NB=int(os.environ.get('NB','4')); PIER=0.70; END=float(os.environ.get('END','2.6'))
BW=(L-2*END-(NB-1)*PIER)/NB
GZ0,GZ1=135.0,142.25; REV=0.22; GREC=0.16; TR=138.88
ops=[]
for i in range(NB):
    a=U0+END+i*(BW+PIER); ops.append((a,a+BW,GZ0,GZ1))
print('bay width',round(BW,2),'ops',[(round(a,2),round(b,2)) for a,b,_,_ in ops])
def V(uu,z,dd=0.0):
    p=P+W*uu+Fn*dd; return Vector((p.x,p.y,z))
vc={}
def gv(uu,z):
    k=(round(uu,4),round(z,4))
    if k not in vc: vc[k]=bm.verts.new(V(uu,z))
    return vc[k]
def face(vs,mat,nn):
    f=bm.faces.new(vs); f.material_index=mat; f.normal_update()
    if f.normal.dot(nn)<0: f.normal_flip()
    return f
ub=sorted(set([U0,U1]+[x for op in ops for x in op[:2]])); zb=[Z0,GZ0,GZ1,Z1]
for i in range(len(ub)-1):
    for j in range(len(zb)-1):
        um=(ub[i]+ub[i+1])/2; zm=(zb[j]+zb[j+1])/2
        if any(a<um<b and c<zm<e for a,b,c,e in ops): continue
        face([gv(ub[i],zb[j]),gv(ub[i+1],zb[j]),gv(ub[i+1],zb[j+1]),gv(ub[i],zb[j+1])],STU,Fn)
def box(u0,u1,z0,z1,d0,d1,mat):
    cs=[bm.verts.new(V(uu,zz,dd)) for uu in (u0,u1) for zz in (z0,z1) for dd in (d0,d1)]
    bc=sum((v.co for v in cs),Vector())/8
    for q in [(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3)]:
        f=bm.faces.new([cs[k] for k in q]); f.material_index=mat; f.normal_update()
        if f.normal.dot(f.calc_center_median()-bc)<0: f.normal_flip()
for a,b,c,e in ops:
    for (uu,nn) in [(a,W),(b,-W)]:
        face([bm.verts.new(V(uu,c)),bm.verts.new(V(uu,e)),bm.verts.new(V(uu,e,-REV)),bm.verts.new(V(uu,c,-REV))],STU,nn)
    for (zz,nn) in [(c,Vector((0,0,1))),(e,Vector((0,0,-1)))]:
        face([bm.verts.new(V(a,zz)),bm.verts.new(V(b,zz)),bm.verts.new(V(b,zz,-REV)),bm.verts.new(V(a,zz,-REV))],STU,nn)
    # back of reveal: glass plane (opaque reflective, no interior modelled)
    face([bm.verts.new(V(a,c,-GREC)),bm.verts.new(V(b,c,-GREC)),bm.verts.new(V(b,e,-GREC)),bm.verts.new(V(a,e,-GREC))],GLA,Fn)
    # perimeter frame 7 cm, mullions 5 cm, transom at floor line
    F=0.07; fd0,fd1=-GREC-0.01,-GREC+0.05
    box(a,a+F,c,e,fd0,fd1,MUL); box(b-F,b,c,e,fd0,fd1,MUL)
    box(a+F,b-F,c,c+F,fd0,fd1,MUL); box(a+F,b-F,e-F,e,fd0,fd1,MUL)
    box(a+F,b-F,TR-0.06,TR+0.06,fd0,fd1+0.01,MUL)
    nm=max(2,round((b-a)/1.05)); 
    for k in range(1,nm):
        x=a+(b-a)*k/nm; box(x-0.025,x+0.025,c+F,e-F,fd0,fd1-0.01,MUL)
    # projecting sill
    box(a-0.06,b+0.06,c-0.07,c+0.006,-REV,0.06,SILL)
bmesh.ops.remove_doubles(bm,verts=list(vc.values()),dist=0.0005)
bm.to_mesh(me); me.update(); bm.free()
o['ws17_east_glazing']='4 double-height bays, UNVERIFIED (Joe aerial A)'
print('BUILT')
for n in ('TZ_Cole_windows_EN_UNVERIFIED','TZ_Cole_sill_drips_EN_UNVERIFIED'):
    ob=bpy.data.objects[n]; bb=[ob.matrix_world@Vector(c) for c in ob.bound_box]
    print('OTHER',n,'hide',ob.hide_render,[round(min(p[i] for p in bb),2) for i in range(3)],[round(max(p[i] for p in bb),2) for i in range(3)])
if os.environ.get('SAVE')=='1':
    bpy.ops.wm.save_mainfile(); print('SAVED')
