# oi (Oct 31 2026): Schmitt wing facade either side of the entrance pavilion (ESE run '(0.92, -0.4, -51)' only, the run the
# pavilion projects from; per schmitt_01/03 the wing beside the pavilion has arched 2F windows in arcade bays between flat piers and
# top-floor window bands under a bracketed eave). Walls are a thin shell, so the 'recessed' arcade is built as proud piers + an
# arcade head band with arch cut-outs (0.13 m proud, closed meshes). 2F og windows -> arched openings (exact boolean, through-cut),
# top row -> wide band openings (4 panes); og SCH_win r1/r2 instances on these bays hidden (not deleted). Other facades untouched.
# Original wall mesh kept as OI_walls_orig_pre_oi (fake user). REVERT=1 restores. ALL sizes UNVERIFIED (estimated from photos).
import bpy, bmesh, json, math, os, sys
from mathutils import Vector, Matrix
REV=os.environ.get('REVERT')=='1'; SAVE='--save' in sys.argv
ROOT=os.path.dirname(bpy.data.filepath); SJ=os.path.join(ROOT,'data/oi/oi_wing_state.json')
CN='OI_Schmitt_wing_arcade_20261031oi'; RUN='(0.92, -0.4, -51)'
w=bpy.data.objects['Schmitt Hall walls']
st=json.load(open(SJ)) if os.path.exists(SJ) else {}
if not st:   # fallback (state json lost by an aborted run): pre-oi these og r1/r2 instances were all visible (pre-oi signature)
    st={'hidden':{o.name:[False,False] for o in bpy.data.objects if o.name.startswith('SCH_win_') and o.get('run')==RUN and o.get('row') in (1,2)}}
c=bpy.data.collections.get(CN)
if c:
    for ob in list(c.objects):
        me=ob.data; bpy.data.objects.remove(ob)
        if me and me.users==0: bpy.data.meshes.remove(me)
    bpy.data.collections.remove(c)
for n,v in st.get('hidden',{}).items():
    o=bpy.data.objects.get(n)
    if o: o.hide_render=v[0]; o.hide_viewport=v[1]
orig=bpy.data.meshes.get('OI_walls_orig_pre_oi')
if orig:
    cur=w.data; nm=cur.name; w.data=orig; bpy.data.meshes.remove(cur); orig.name=nm; orig.use_fake_user=False
for n in [m.name for m in bpy.data.materials if m.name.startswith('OI_Schmitt_wing_')]: bpy.data.materials.remove(bpy.data.materials[n])
if os.path.exists(SJ): os.remove(SJ)
if REV:
    print('REVERTED')
    if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
    raise SystemExit(0)
st={'hidden':{}}
bpy.context.view_layer.update()
cells=[o for o in bpy.data.objects if o.name.startswith('SCH_win_') and o.get('run')==RUN and o.get('row')==1]
M0=cells[0].matrix_world; T=Vector((M0[0][0],M0[1][0],0)).normalized(); Nn=Vector((M0[0][1],M0[1][1],0)).normalized()
O0=M0.translation.copy(); O0.z=0; N_ref=Nn.copy(); T_ref=T.copy()
def uv(p): d=p-O0; return d.dot(T), d.dot(Nn)
# per straight wall (group) frames: the run is two slightly different walls either side of the pavilion
cps=sorted([o.matrix_world.translation.copy() for o in cells],key=lambda q:(q-O0).dot(T_ref))
GR=[[cps[0]]]
for q in cps[1:]:
    if (q-GR[-1][-1]).length<3.7: GR[-1].append(q)
    else: GR.append([q])
FR=[]
for g in GR:
    a_,b_=g[0],g[-1]; t=Vector(((b_-a_).x,(b_-a_).y,0)).normalized(); n=Vector((t.y,-t.x,0))
    if n.dot(N_ref)<0: n=-n
    o=a_.copy(); o.z=0; FR.append((o,t,n,[round((q-o).dot(t),3) for q in g]))
    print('group frame', [round(x,3) for x in o], 'n spread',[round((q-o).dot(n),3) for q in g])
wf=0.0
def setf(k):
    global O0,T,Nn,us,groups
    O0,T,Nn,us=FR[k][0],FR[k][1],FR[k][2],FR[k][3]; groups=[us]
def P(u,n,z): return O0+T*u+Nn*(wf+n)+Vector((0,0,z))
ter=bpy.data.objects['Terrain_LiDAR_DTM_1m']; tmi=ter.matrix_world.inverted()
def tz(p):
    h,l,n_,i=ter.ray_cast(tmi@Vector((p.x,p.y,400)),tmi.to_3x3()@Vector((0,0,-1))); return (ter.matrix_world@l).z if h else 135.0
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
def wall_at(u,z):
    mi=w.matrix_world.inverted(); o=P(u,1.0,z); h,l,n_,i=w.ray_cast(mi@o,(mi.to_3x3()@(-Nn)).normalized(),distance=1.6); return h
eave=bpy.data.objects['Schmitt Hall eave soffit + fascia + rafter tails']
def soffit(u):
    o=P(u,0.35,146.5); h,l,n_,i,ob,m=sc.ray_cast(dg,o,Vector((0,0,1)),distance=4); print('soffit ray',round(u,1),h,ob.name if ob else None,round(l.z,2) if h else None); return l.z if h and ob==eave else None
# materials
red=bpy.data.materials['OH_Schmitt_win_frame_red_brown']; gl=bpy.data.materials['OH_Schmitt_door_glass_clear_UNVERIFIED']
stu=bpy.data.materials['OH_Schmitt_stucco_block_base_UNVERIFIED']
soff=bpy.data.materials.get('OI_Schmitt_overhang_red_UNVERIFIED') or red
bk=bpy.data.materials.new('OI_Schmitt_wing_room_interior_dim_UNVERIFIED'); bk.use_nodes=True; p_=bk.node_tree.nodes['Principled BSDF']
p_.inputs['Base Color'].default_value=(0.12,0.10,0.085,1); p_.inputs['Emission Color'].default_value=(1,0.75,0.5,1); p_.inputs['Emission Strength'].default_value=0.05
col=bpy.data.collections.new(CN); sc.collection.children.link(col)
def newobj(name,bm,m,facade=False):
    me=bpy.data.meshes.new(name); bm.to_mesh(me); bm.free(); me.materials.append(m)
    if facade:
        ul=me.uv_layers.new(name='facade')
        for d in ul.data: d.uv=(0.0,-1000.0)
    o=bpy.data.objects.new(name,me); col.objects.link(o); o['UNVERIFIED']='oi: arcade/arch/band sizes estimated from schmitt_01/03'; return o
def prism(bm,prof,n0,n1):
    a=[bm.verts.new(P(u,n0,z)) for u,z in prof]; b=[bm.verts.new(P(u,n1,z)) for u,z in prof]
    bm.faces.new(a); bm.faces.new(b[::-1])
    for i in range(len(prof)): j=(i+1)%len(prof); bm.faces.new([a[i],a[j],b[j],b[i]])
def box(bm,u0,u1,n0,n1,z0,z1): prism(bm,[(u0,z0),(u1,z0),(u1,z1),(u0,z1)],n0,n1)
def bar(bm,p0,p1,wd,n0,n1):
    (a0,z0),(a1,z1)=p0,p1; d=Vector((a1-a0,z1-z0)); L=d.length; d/=L; q=Vector((-d.y,d.x))*wd/2; e=d*wd/2
    prism(bm,[(a0+q.x-e.x,z0+q.y-e.y),(a0-q.x-e.x,z0-q.y-e.y),(a1-q.x+e.x,z1-q.y+e.y),(a1+q.x+e.x,z1+q.y+e.y)],n0,n1)
def fix(bm): bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
AH=1.05; ZS=144.45; ZW0=142.55; NA=20   # arched window half-width, spring, sill
BH=1.45; BZ0=146.20; BZ1=148.10           # top band
RA=1.35; HZ1=146.15; PW=0.47; PR=0.13      # arcade radius, head top, pier half-width, projection
def archprof(h,zs,z0,n=NA): return [(-h,z0),(h,z0)]+[(h*math.cos(math.pi*i/n),zs+h*math.sin(math.pi*i/n)) for i in range(n+1)]
# hide og r1/r2 on these bays (state written at once so an aborted run can't lose it)
for o in bpy.data.objects:
    if o.name.startswith('SCH_win_') and o.get('run')==RUN and o.get('row') in (1,2):
        st['hidden'][o.name]=[o.hide_render,o.hide_viewport]; o.hide_render=True; o.hide_viewport=True
json.dump(st,open(SJ,'w'),indent=1)
# wall cut
cb=bmesh.new()
for k in range(len(FR)):
  setf(k)
  for u in us:
    prism(cb,[(u+a,z) for a,z in archprof(AH,ZS,ZW0)],-0.6,0.6)
    box(cb,u-BH,u+BH,-0.6,0.6,BZ0,BZ1)
fix(cb); cme=bpy.data.meshes.new('OI_wcut_tmp'); cb.to_mesh(cme); cb.free(); cut=bpy.data.objects.new('OI_wcut_tmp',cme); col.objects.link(cut)
o2=w.data.copy(); o2.name='OI_walls_orig_pre_oi'; o2.use_fake_user=True
md=w.modifiers.new('oi_cut','BOOLEAN'); md.operation='DIFFERENCE'; md.solver='EXACT'; md.object=cut
try: md.use_hole_tolerant=True
except Exception: pass
nf0=len(w.data.polygons)
with bpy.context.temp_override(object=w,active_object=w,selected_objects=[w]): bpy.ops.object.modifier_apply(modifier=md.name)
bpy.data.objects.remove(cut); bpy.data.meshes.remove(cme); print('wall faces',nf0,'->',len(w.data.polygons))
# piers + arcade head
bm=bmesh.new(); hb=bmesh.new(); npier=0; OKS={}
for k in range(len(FR)):
  setf(k); g=us
  if True:
    pu=[g[0]-1.8]+[(a+b)/2 for a,b in zip(g,g[1:])]+[g[-1]+1.8]
    ok=[x for x in pu if wall_at(x,141.0)]; OKS[k]=ok
    for x in ok:
        gz=min(tz(P(x,0.0,0)),tz(P(x,PR+0.05,0)))-0.3
        box(bm,x-PW,x+PW,-0.02,PR,gz,ZS+0.05); npier+=1
    u0=min(ok); u1=max(ok); box(hb,u0-PW,u1+PW,-0.02,PR,ZS,HZ1)
fix(bm); newobj('OI_Schmitt_wing_arcade_piers',bm,stu,True)
fix(hb); head=newobj('OI_Schmitt_wing_arcade_head_band',hb,stu,True)
cb=bmesh.new()
for k in range(len(FR)):
  setf(k)
  for u in us: prism(cb,[(u+a,z) for a,z in archprof(RA,ZS,ZS-0.3)],-0.3,PR+0.3)
fix(cb); cme=bpy.data.meshes.new('OI_hcut_tmp'); cb.to_mesh(cme); cb.free(); cut=bpy.data.objects.new('OI_hcut_tmp',cme); col.objects.link(cut)
md=head.modifiers.new('c','BOOLEAN'); md.operation='DIFFERENCE'; md.solver='EXACT'; md.object=cut
with bpy.context.temp_override(object=head,active_object=head,selected_objects=[head]): bpy.ops.object.modifier_apply(modifier=md.name)
bpy.data.objects.remove(cut); bpy.data.meshes.remove(cme)
print('piers',npier)
# arched windows + bands: reveal liners, frames, glass, interior backing
fb=bmesh.new(); gb=bmesh.new(); ib=bmesh.new(); rb=bmesh.new()
FN0,FN1=-0.13,-0.05
for u,k in [(u,k) for k in range(len(FR)) for u in FR[k][3]]:
    setf(k)
    pr=[(u+a,z) for a,z in archprof(AH,ZS,ZW0)]
    # reveal liner: ring between the opening outline and a 3 cm larger outline, depth wall face +0.01 .. -0.25
    po=[(u+a,z) for a,z in archprof(AH+0.03,ZS,ZW0-0.03)]
    for k in range(len(pr)):
        j=(k+1)%len(pr)
        q=[rb.verts.new(P(*pr[k][:1],-0.25,pr[k][1])) if False else None]
    a=[rb.verts.new(P(x,n,z)) for n in (0.01,-0.25) for x,z in pr]; b=[rb.verts.new(P(x,n,z)) for n in (0.01,-0.25) for x,z in po]
    L=len(pr)
    for k in range(L):
        j=(k+1)%L
        rb.faces.new([a[k],a[j],a[L+j],a[L+k]]); rb.faces.new([b[L+k],b[L+j],b[j],b[k]])
        rb.faces.new([a[j],a[k],b[k],b[j]]); rb.faces.new([a[L+k],a[L+j],b[L+j],b[L+k]])
    for p0_,p1_ in zip(pr[2:],pr[3:]): bar(fb,p0_,p1_,0.09,FN0,FN1)
    for s in (-1,1): bar(fb,(u+s*(AH-0.045),ZW0),(u+s*(AH-0.045),ZS),0.09,FN0,FN1)
    bar(fb,(u-AH,ZW0+0.045),(u+AH,ZW0+0.045),0.09,FN0,FN1); bar(fb,(u-AH+0.05,ZS),(u+AH-0.05,ZS),0.08,FN0,FN1); bar(fb,(u-AH+0.05,143.50),(u+AH-0.05,143.50),0.06,FN0,FN1)
    for s in (-0.36,0.36): bar(fb,(u+s,ZW0),(u+s,ZS+math.sqrt(AH**2-s**2)-0.04),0.06,FN0,FN1)
    prism(gb,[(x,z) for x,z in pr],-0.095,-0.085)
    prism(ib,[(x,z) for x,z in pr],-0.62,-0.60)
    # band window
    pb=[(u-BH,BZ0),(u+BH,BZ0),(u+BH,BZ1),(u-BH,BZ1)]
    a=[rb.verts.new(P(x,n,z)) for n in (0.01,-0.25) for x,z in pb]; pbo=[(u-BH-0.03,BZ0-0.03),(u+BH+0.03,BZ0-0.03),(u+BH+0.03,BZ1+0.03),(u-BH-0.03,BZ1+0.03)]
    b=[rb.verts.new(P(x,n,z)) for n in (0.01,-0.25) for x,z in pbo]
    for k in range(4):
        j=(k+1)%4
        rb.faces.new([a[k],a[j],a[4+j],a[4+k]]); rb.faces.new([b[4+k],b[4+j],b[j],b[k]]); rb.faces.new([a[j],a[k],b[k],b[j]]); rb.faces.new([a[4+k],a[4+j],b[4+j],b[4+k]])
    box(fb,u-BH,u+BH,FN0,FN1,BZ0,BZ0+0.09); box(fb,u-BH,u+BH,FN0,FN1,BZ1-0.09,BZ1)
    for s in (-1,1): box(fb,u+s*BH-(0.09 if s>0 else 0),u+s*BH+(0.09 if s<0 else 0),FN0,FN1,BZ0,BZ1)
    for k in (1,2,3): x=u-BH+k*2*BH/4; bar(fb,(x,BZ0),(x,BZ1),0.07,FN0,FN1)
    bar(fb,(u-BH,147.55),(u+BH,147.55),0.06,FN0,FN1)
    prism(gb,pb,-0.095,-0.085); prism(ib,pb,-0.62,-0.60)
for b_ in (fb,gb,ib,rb): fix(b_)
newobj('OI_Schmitt_wing_arched_and_band_window_frames',fb,red)
newobj('OI_Schmitt_wing_arched_and_band_window_glass',gb,gl)
newobj('OI_Schmitt_wing_window_room_interior_backing',ib,bk)
newobj('OI_Schmitt_wing_window_reveal_liners',rb,stu,True)
# eave brackets at the piers (under the existing soffit)
bb=bmesh.new(); nb=0
for k in range(len(FR)):
  setf(k); g=us
  if True:
    for x in OKS[k]:
        sz=soffit(x)
        if sz is None or sz<146.6 or sz>149.5: continue
        vs=[]
        for z,ln in ((sz-0.70,0.16),(sz+0.01,0.72)):
            for a_,n_ in ((x-0.09,-0.02),(x+0.09,-0.02),(x+0.09,ln),(x-0.09,ln)): vs.append(bb.verts.new(P(a_,n_,z)))
        for f in ((0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)): bb.faces.new([vs[i] for i in f])
        nb+=1
fix(bb); newobj('OI_Schmitt_wing_eave_brackets',bb,soff); print('brackets',nb)
json.dump(st,open(SJ,'w'),indent=1); print('hidden',len(st['hidden']))
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
