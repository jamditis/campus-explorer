"""vt pass 2: raised entrance landing + 4 steps up from grade + orange pipe rails + short paved link (slide 1096). UNVERIFIED."""
import bpy, bmesh, json
from mathutils import Vector as V
log=json.load(open('/workspace/nj-scenes/montclair-state/data/vt/vt_main.json'))
PW=V(log['PW']); PE=V(log['PE'])
d=V((-0.974,0.228,0)).normalized(); out=V((0.228,0.974,0)).normalized(); inn=-out
ZL=130.40; ZG=129.76; R=(ZL-ZG)/4; T=0.32; LAND=1.2; DEPTH=0.74
col=bpy.data.collections['VT_Freeman_N_entrance_recess_UNVERIFIED']
conc=bpy.data.materials['UV_Freeman_step_concrete_UNVERIFIED']
org=bpy.data.materials['UV_Freeman_orange_panel_rail_UNVERIFIED']
new=[]
def box(name,pts,mat):
    me=bpy.data.meshes.new(name); bm=bmesh.new(); vv=[bm.verts.new(p) for p in pts]
    for f in [(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)]: bm.faces.new([vv[i] for i in f])
    bmesh.ops.recalc_face_normals(bm,faces=bm.faces); bm.to_mesh(me); bm.free(); me.materials.append(mat)
    o=bpy.data.objects.new(name,me); col.objects.link(o); o['vt_obj']=1; new.append(name); return o
def slab(p0,p1,z0,z1,o0,o1,mat,name):
    q=[p0+out*o0,p1+out*o0,p1+out*o1,p0+out*o1]
    return box(name,[V((a.x,a.y,z0)) for a in q]+[V((a.x,a.y,z1)) for a in q],mat)
# old floor -> raise; old UV steps hide
f=bpy.data.objects['VT_Freeman_N_entrance_floor_UNVERIFIED']; bpy.data.objects.remove(f)
st=bpy.data.objects['UV_Freeman_N_entrance_steps_handrails_UNVERIFIED']; st.hide_render=True; st.hide_viewport=True; st['vt_hidden']=1
slab(PW,PE,ZG-0.3,ZL,-DEPTH,LAND,conc,'VT_Freeman_N_entrance_landing_UNVERIFIED')
for i in range(4):
    zt=ZL-R*(i+1)
    slab(PW,PE,ZG-0.3,zt,LAND+T*i,LAND+T*(i+1),conc,'VT_Freeman_N_entrance_step_%d_UNVERIFIED'%(i+1))
run_end=LAND+T*4
# short paved link to the OZ walk (judgment; photo shows paving at the step foot)
lw=bpy.data.materials.get('OZ_walk_concrete_UNVERIFIED') or conc
slab(PW-d*0.3,PE+d*0.3,ZG-0.3,ZG+0.045,run_end,run_end+1.4,conc,'VT_Freeman_N_entrance_step_foot_paving_UNVERIFIED')
# rails: per side, posts + sloped top rail + landing return
def rod(a,b,r,name):
    ax=(b-a); L=ax.length; z=ax.normalized()
    x=z.cross(V((0,0,1))) if abs(z.z)<0.95 else z.cross(V((1,0,0))); x.normalize(); y=z.cross(x)
    pts=[a+(x*sx+y*sy)*r for sx,sy in [(-1,-1),(1,-1),(1,1),(-1,1)]]
    pts+= [p+ax for p in pts]
    return box(name,pts,org)
H=0.92
for side,base in [('W',PW+d*0.18),('E',PE-d*0.18)]:
    top0=base+out*(LAND-0.25); top1=base+out*(run_end-0.1)
    z0=ZL; z1=ZG+R*0.5
    rod(V((top0.x,top0.y,z0+H)),V((top1.x,top1.y,z1+H)),0.022,'VT_Freeman_N_rail_%s_top'%side)
    rod(V((top0.x,top0.y,z0+0.55)),V((top1.x,top1.y,z1+0.55)),0.016,'VT_Freeman_N_rail_%s_mid'%side)
    back=base+out*0.15
    rod(V((back.x,back.y,z0+H)),V((top0.x,top0.y,z0+H)),0.022,'VT_Freeman_N_rail_%s_land'%side)
    for k,(p,z) in enumerate([(back,z0),(top0,z0),(top1,z1)]):
        rod(V((p.x,p.y,z)),V((p.x,p.y,z+H+0.02)),0.025,'VT_Freeman_N_rail_%s_post%d'%(side,k))
# shift curtain doors up to the landing; clamp under roof
c=bpy.data.objects['UV_Freeman_N_entrance_curtain_doors_canopy_UNVERIFIED']; mw=c.matrix_world; mi=mw.inverted()
sh=ZL-129.10; c['vt_shift']=sh
for v in c.data.vertices:
    w=mw@v.co; w.z=min(w.z+sh,146.85); v.co=mi@w
c.data.update()
log['pass2_new']=new; log['curtain_shift']=sh
json.dump(log,open('/workspace/nj-scenes/montclair-state/data/vt/vt_main.json','w'),indent=1,default=str)
print('VT2',len(new),sh)
bpy.ops.wm.save_as_mainfile(filepath='/workspace/nj-scenes/montclair-state/montclair_state.blend')
