import bpy, bmesh, math
from mathutils import Vector
TZ=bpy.data.objects['TZ_Cole_north_addition_UNVERIFIED']; mw=TZ.matrix_world; nm=mw.to_3x3()
me=TZ.data
a=math.radians(-13.5); U=Vector((math.cos(a),math.sin(a),0)); V=Vector((-math.sin(a),math.cos(a),0))
mats=[s.material.name if s.material else '' for s in TZ.material_slots]
# wall plane from face 2 (front panel)
f2=me.polygons[2]
P=[mw@me.vertices[i].co for i in f2.vertices]
n=(nm@f2.normal).normalized(); n.z=0; n.normalize()
out = n if n.dot(V)>0 else -n
h = Vector((out.y,-out.x,0)).normalized()
if h.dot(U)<0: h=-h
c0 = sum(P,Vector())/len(P)
print('WALL out',out,'h',h,'c0',c0)
# 1) delete front glass + mullion faces (all verts in front of wall plane - 0.25)
bm=bmesh.new(); bm.from_mesh(me); bm.faces.ensure_lookup_table()
kill=[]
for f in bm.faces:
  mn=mats[f.material_index]
  if 'glass' in mn or 'mullion' in mn:
    ds=[(mw@vv.co - c0).dot(out) for vv in f.verts]
    if min(ds)>-0.25: kill.append(f)
print('KILL faces',len(kill))
bmesh.ops.delete(bm,geom=kill,context='FACES')
# front panel -> Cole stucco, normal outward
st=bpy.data.materials['COLE_stucco_plain_bq']
if st.name not in [s.material.name for s in TZ.material_slots if s.material]:
  me.materials.append(st)
si=[s.material.name if s.material else '' for s in TZ.material_slots].index(st.name)
bm.faces.ensure_lookup_table()
f=bm.faces[2]; f.material_index=si
if (nm@f.normal).dot(out)<0: f.normal_flip()
bm.to_mesh(me); bm.free(); me.update()
# 2) arched window object
gl=bpy.data.materials['TZ_Cole_add_glass_UNVERIFIED']; tr=bpy.data.materials['COLE_win_trim_white_br']
# window centre along h: gable centre from panel extents
hs=[(p-c0).dot(h) for p in P]; zs=[p.z for p in P]
hc=(min(hs)+max(hs))/2; z0=min(zs)
W=3.6; R=W/2; zb=z0+0.35; zspring=z0+7.6
print('PANEL h',min(hs),max(hs),'z',z0,max(zs),'hc',hc)
def pt(x,z,d): return c0 + h*(hc+x) + out*d + Vector((0,0,z-c0.z))
def outline(r_off, N=24):
  w=R+r_off; pts=[(-w,zb-r_off),(w,zb-r_off)]
  for i in range(N+1):
    t=math.pi*i/N; pts.append((w*math.cos(t), zspring+w*math.sin(t)))
  return pts
bm=bmesh.new()
def ring(inner,outer,d0,d1,mi):
  n=len(inner)
  vi0=[bm.verts.new(pt(x,z,d0)) for x,z in inner]; vi1=[bm.verts.new(pt(x,z,d1)) for x,z in inner]
  vo0=[bm.verts.new(pt(x,z,d0)) for x,z in outer]; vo1=[bm.verts.new(pt(x,z,d1)) for x,z in outer]
  for i in range(n):
    j=(i+1)%n
    for q in ((vi1[i],vi1[j],vo1[j],vo1[i]),(vo0[i],vo0[j],vo1[j],vo1[i]),(vi0[i],vi1[i],vi1[j],vi0[j])):
      bm.faces.new(q).material_index=mi
def box(x0,x1,za,zb_,d0,d1,mi):
  vs=[bm.verts.new(pt(x,z,d)) for x in (x0,x1) for z in (za,zb_) for d in (d0,d1)]
  for q in ((0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(1,5,7,3),(0,2,6,4)):
    bm.faces.new([vs[k] for k in q]).material_index=mi
# glass panel (inset)
g=[bm.verts.new(pt(x,z,0.05)) for x,z in outline(0.0)]
bm.faces.new(g).material_index=0
# frame (white trim) 0.14 wide, proud 0.05->0.16 ; outer stucco surround 0.30 wide 0.0->0.10
ring(outline(0.0),outline(0.14),0.05,0.16,1)
ring(outline(0.14),outline(0.44),0.0,0.10,2)
# muntins: two verticals + spring-line transom + door transom, keystone, sill
for x in (-R/3,R/3):
  box(x-0.05,x+0.05,zb,zspring+math.sqrt(max(R*R-x*x,0))-0.02,0.05,0.12,1)
box(-R,R,zspring-0.06,zspring+0.06,0.05,0.12,1)
box(-R,R,zb+2.55,zb+2.67,0.05,0.13,1)   # door head transom (door set UNVERIFIED)
box(-0.08,0.08,zb,zb+2.55,0.05,0.13,1)  # door meeting stile
box(-0.30,0.30,zspring+R+0.10,zspring+R+0.75,0.0,0.16,2)  # keystone
box(-R-0.5,R+0.5,zb-0.55,zb-0.35,0.0,0.22,2) if False else None
wm=bpy.data.meshes.new('WS6_Cole_gable_arched_window_UNVERIFIED')
bm.to_mesh(wm); bm.free()
for m in (gl,tr,st): wm.materials.append(m)
ob=bpy.data.objects.new('WS6_Cole_gable_arched_window_UNVERIFIED',wm)
col=bpy.data.collections.new('WS6_Cole_gable_front_20261109'); bpy.context.scene.collection.children.link(col); col.objects.link(ob)
for p in wm.polygons: p.use_smooth=False
# camera
cd=bpy.data.cameras.new('WS6_CAM_eye_cole_gable_from_plaza'); cam=bpy.data.objects.new(cd.name,cd); col.objects.link(cam)
tgt=pt(0,z0+5.5,0); loc=tgt+out*24+Vector((0,0,0))+h*3; loc.z=z0+1.7
cam.location=loc; cd.lens=24; cd.clip_start=0.1; cd.clip_end=3000
cam.rotation_euler=(tgt-loc).to_track_quat('-Z','Y').to_euler()
print('CAM',loc,tgt)
bpy.ops.wm.save_mainfile()
print('SAVED')
