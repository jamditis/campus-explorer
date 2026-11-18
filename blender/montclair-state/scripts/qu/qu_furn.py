# qu (2): ground-storey furniture behind the Richardson glass, from existing kits (assets/student_lounge_counter_kit_oa.blend,
# furniture_kit_nr.blend, shell_chair_kit_nt.blend). Generic lounge/cafe clusters, UNVERIFIED (no interior photos).
# Merged into 1 mesh in collection QU_Richardson_interior_hint_UNVERIFIED (removed by qu_main REVERT). Run after qu_main.
import bpy,json,math,random,os
from mathutils import Vector,Matrix
A='/workspace/nj-scenes/assets/'
KITS={'student_lounge_counter_kit_oa.blend':['KIT_lounge_chair_crimson','KIT_lounge_chair_charcoal','KIT_low_table_1000','KIT_sofa_2seat'],
      'furniture_kit_nr.blend':['KIT_cafe_pedestal_table_800'],'shell_chair_kit_nt.blend':['KIT_moulded_shell_chair_4leg_white','KIT_moulded_shell_chair_4leg_orange']}
parts={}; tmpobjs=[]
for f,pre in KITS.items():
    with bpy.data.libraries.load(A+f) as (src,dst):
        dst.objects=[n for n in src.objects if any(n==p or n.startswith(p+' ') for p in pre)]
    for o in dst.objects:
        if o is None: continue
        tmpobjs.append(o)
        key=[p for p in pre if o.name==p or o.name.startswith(p+' ')][0]
        parts.setdefault(key,[]).append(o)
for m in bpy.data.materials:
    if m.library is None and m.users and not m.name.startswith('QU_') and any(m.name in [s.material.name for s in o.material_slots if s.material] for o in tmpobjs):
        pass
# rename appended kit materials so revert can find them (only those used solely by the temp objects)
used_elsewhere=set()
for o in bpy.data.objects:
    if o in tmpobjs: continue
    for s in o.material_slots:
        if s.material: used_elsewhere.add(s.material)
for o in tmpobjs:
    for s in o.material_slots:
        m=s.material
        if m and m not in used_elsewhere and not m.name.startswith('QU_'): m.name='QU_kit_'+m.name
def wm(o):  # world matrix incl. parents (kit parents are not appended -> use matrix_world as stored)
    return o.matrix_world.copy()
# kit local frames: floor z=0, sitter faces -X. Compute each kit's xy centre so we can place it.
def kit_centre(k):
    xs=[];ys=[];zs=[]
    for o in parts[k]:
        for c in o.bound_box:
            p=wm(o)@Vector(c); xs.append(p.x); ys.append(p.y); zs.append(p.z)
    return Vector(((min(xs)+max(xs))/2,(min(ys)+max(ys))/2,min(zs)))
C={k:kit_centre(k) for k in parts}
print('QUF kits',{k:len(v) for k,v in parts.items()})
P=json.load(open('data/qu/interior_polys_qu.json')); ring=P['G_slab']; n=len(ring)
ccw=sum(ring[i][0]*ring[(i+1)%n][1]-ring[(i+1)%n][0]*ring[i][1] for i in range(n))>0
DOORS=[Vector((74.64,242.13)),Vector((79.95,290.37))]
random.seed(1102)
V=[];F=[];FM=[];mats=[]
def add(k,loc,yaw):
    M=Matrix.Translation(loc)@Matrix.Rotation(yaw,4,'Z')@Matrix.Translation(-C[k])
    for o in parts[k]:
        me=o.data; T=M@wm(o); base=len(V)
        V.extend([tuple(T@v.co) for v in me.vertices])
        sl=[s.material for s in o.material_slots]
        for p in me.polygons:
            F.append([base+i for i in p.vertices]); m=sl[p.material_index] if sl else None
            if m not in mats: mats.append(m)
            FM.append(mats.index(m))
nc=0
for i in range(n):
    a=Vector(ring[i]); b=Vector(ring[(i+1)%n]); d=b-a; Ln=d.length
    if Ln<5: continue
    d.normalize(); inn=Vector((-d.y,d.x)) if ccw else Vector((d.y,-d.x))
    k=int(Ln//6.5)
    for t in range(k):
        s=(t+0.5+random.uniform(-0.15,0.15))*Ln/k; p=a+d*s
        if min((p-q).length for q in DOORS)<4.0: continue
        face=math.atan2(-inn.y,-inn.x)  # sitter faces -X -> rotate so the seat faces the glass/out
        base=p+inn*random.uniform(2.6,3.4); z=136.68
        if random.random()<0.5:  # lounge: low table + 2 chairs facing each other across it, sofa behind
            add('KIT_low_table_1000',Vector((base.x,base.y,z)),face)
            for sgn,kk in ((1,'KIT_lounge_chair_crimson'),(-1,random.choice(['KIT_lounge_chair_charcoal','KIT_lounge_chair_crimson']))):
                q=base+d*sgn*1.15; add(kk,Vector((q.x,q.y,z)),math.atan2(d.y*sgn,d.x*sgn))
            if random.random()<0.6:
                q=base+inn*1.2; add('KIT_sofa_2seat',Vector((q.x,q.y,z)),math.atan2(inn.y,inn.x))
        else:  # cafe: pedestal table + 2-3 shell chairs
            add('KIT_cafe_pedestal_table_800',Vector((base.x,base.y,z)),0)
            ch=random.choice(['KIT_moulded_shell_chair_4leg_white','KIT_moulded_shell_chair_4leg_orange'])
            for ang in random.sample([0,1.57,3.14,4.71],random.choice([2,3])):
                dirv=Vector((math.cos(ang+0.3),math.sin(ang+0.3))); q=base+dirv*0.62
                add(ch,Vector((q.x,q.y,z)),math.atan2(dirv.y,dirv.x))
        nc+=1
me=bpy.data.meshes.new('QU_G_furniture'); me.from_pydata(V,[],F); me.update()
for m in mats: me.materials.append(m)
for p,mi in zip(me.polygons,FM): p.material_index=mi
for p in me.polygons: p.use_smooth=False
o=bpy.data.objects.new('QU_G_furniture_UNVERIFIED',me); bpy.data.collections['QU_Richardson_interior_hint_UNVERIFIED'].objects.link(o)
o['UNVERIFIED_qu']='generic lounge/cafe clusters from the oa/nr/nt kits; no interior photos'
for t in tmpobjs:
    d=t.data; bpy.data.objects.remove(t,do_unlink=True)
    if d and d.users==0: bpy.data.meshes.remove(d)
print('QUF clusters',nc,'verts',len(V),'faces',len(F),'mats',[m.name if m else None for m in mats])
if os.environ.get('QUSAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')
