import bpy, bmesh, math, random
from mathutils import Vector
kit=bpy.data.collections.new('WS7_Cole_gable_base_and_bed_20261109'); bpy.context.scene.collection.children.link(kit)
TZ=bpy.data.objects['TZ_Cole_north_addition_UNVERIFIED']; mw=TZ.matrix_world; nm=mw.to_3x3(); me=TZ.data
a=math.radians(-13.5); U=Vector((math.cos(a),math.sin(a),0)); V=Vector((-math.sin(a),math.cos(a),0))
f2=me.polygons[2]; P=[mw@me.vertices[i].co for i in f2.vertices]
n=(nm@f2.normal).normalized(); n.z=0; n.normalize(); out=n if n.dot(V)>0 else -n
h=Vector((out.y,-out.x,0)).normalized()
if h.dot(U)<0: h=-h
c0=sum(P,Vector())/len(P); hs=[(p-c0).dot(h) for p in P]; zs=[p.z for p in P]; hc=(min(hs)+max(hs))/2; z0=min(zs)
print('PANEL',min(hs),max(hs),z0,max(zs),'out',out)
# window centre along h from window object
w=bpy.data.objects['WS6_Cole_gable_arched_window_UNVERIFIED']; wv=[w.matrix_world@v.co for v in w.data.vertices]
wh=[(p-c0).dot(h) for p in wv]; whc=(min(wh)+max(wh))/2; whalf=(max(wh)-min(wh))/2
print('WIN h',min(wh),max(wh))
# ground height along the wall foot: ray cast down from 0.6 m in front of the wall
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
def ground(x):
  o=c0+h*x+out*0.6; o.z=160
  ok,loc,nn,i,ob,m=sc.ray_cast(dg,o,Vector((0,0,-1)))
  return (loc.z,ob.name) if ok else (None,None)
for x in (min(hs)+0.5, hc-6, whc, hc+6, max(hs)-0.5): print('GROUND',round(x,2),ground(x))
gz=[ground(x)[0] for x in [min(hs)+0.5+i*(max(hs)-min(hs)-1)/10 for i in range(11)]]
gz=[g for g in gz if g]; gtop=max(gz)
zt=gtop+0.55
mat=bpy.data.materials.new('WS7_Cole_base_course_limestone_UNVERIFIED'); mat.use_nodes=True
b=mat.node_tree.nodes['Principled BSDF']; b.inputs['Base Color'].default_value=(0.62,0.6,0.56,1); b.inputs['Roughness'].default_value=0.8
cap=bpy.data.materials.new('WS7_Cole_splash_band_UNVERIFIED'); cap.use_nodes=True
b2=cap.node_tree.nodes['Principled BSDF']; b2.inputs['Base Color'].default_value=(0.55,0.53,0.5,1); b2.inputs['Roughness'].default_value=0.85
me2=bpy.data.meshes.new('WS7_Cole_gable_base_course_UNVERIFIED'); ob=bpy.data.objects.new(me2.name,me2); kit.objects.link(ob)
me2.materials.append(mat); me2.materials.append(cap)
bm=bmesh.new()
def pt(x,z,d): return c0+h*x+out*d+Vector((0,0,z-c0.z))
def box(x0,x1,za,zb,d0,d1,mi):
  vs=[bm.verts.new(pt(x,z,d)) for x in (x0,x1) for z in (za,zb) for d in (d0,d1)]
  for q in ((0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(1,5,7,3),(0,2,6,4)):
    bm.faces.new([vs[k] for k in q]).material_index=mi
gap=whalf+0.12
segs=[(min(hs)+0.02, whc-gap),(whc+gap, max(hs)-0.02)]
for x0,x1 in segs:
  box(x0,x1,z0,zt,-0.02,0.07,0)          # plinth, 7 cm proud
  box(x0,x1,zt,zt+0.06,-0.02,0.10,0)     # projecting cap / water table
bm.to_mesh(me2); bm.free()
for p in me2.polygons: p.use_smooth=False
print('BASE top',zt,'segs',segs)
# shrubs in the ws4 sign bed: real mesh objects sharing the scene's shrub_proto meshes
bed=bpy.data.objects['WS4_Planting_bed_mulch_at_Cole_sign_UNVERIFIED']
vs=[bed.matrix_world@v.co for v in bed.data.vertices]
cx=sum(v.x for v in vs)/len(vs); cy=sum(v.y for v in vs)/len(vs)
# bed long axis via PCA-lite
xs=[v.x-cx for v in vs]; ys=[v.y-cy for v in vs]
sxx=sum(x*x for x in xs); syy=sum(y*y for y in ys); sxy=sum(x*y for x,y in zip(xs,ys))
ang=0.5*math.atan2(2*sxy,sxx-syy); ax=Vector((math.cos(ang),math.sin(ang),0)); ay=Vector((-ax.y,ax.x,0))
print('BED c',cx,cy,'axis deg',math.degrees(ang))
random.seed(7)
protos=[bpy.data.meshes[n] for n in ('shrub_proto_0','shrub_proto_1','shrub_proto_2')]
bedmi=bed.matrix_world.inverted()
for k,(u,v,s) in enumerate([(-1.25,0.1,0.85),(-0.4,-0.15,0.7),(0.45,0.12,0.8),(1.3,-0.1,0.65)]):
  p=Vector((cx,cy,0))+ax*u+ay*v
  ok,loc,nn,i=bed.ray_cast(bedmi@Vector((p.x,p.y,300)),Vector((0,0,-1)))
  if not ok: print('MISS',k); continue
  z=(bed.matrix_world@loc).z
  o=bpy.data.objects.new(f'WS7_Shrub_in_ws4_sign_bed_{k}_UNVERIFIED',protos[k%3]); kit.objects.link(o)
  o.location=(p.x,p.y,z-0.04); o.rotation_euler=(0,0,random.uniform(0,6.28)); o.scale=(s,s,s*random.uniform(0.85,1.0))
  print('SHRUB',k,o.location[:])
# close-up camera on the bed from the south-east (walk side)
cd=bpy.data.cameras.new('WS7_CAM_closeup_ws4_bed_from_S'); cam=bpy.data.objects.new(cd.name,cd); kit.objects.link(cam)
tgt=Vector((cx,cy,135.2)); 
for back in (7.0,6.0,5.0,8.5):
  cl=tgt+Vector((1.8,-back,0)); ok,loc,_,_,ob_,_=sc.ray_cast(dg,Vector((cl.x,cl.y,170)),Vector((0,0,-1)))
  if ok: cam.location=(cl.x,cl.y,loc.z+1.6); break
cd.lens=30
cam.rotation_euler=(tgt-cam.location).to_track_quat('-Z','Y').to_euler()
# close-up camera on the base course + window foot
cd2=bpy.data.cameras.new('WS7_CAM_closeup_gable_base_from_plaza'); cam2=bpy.data.objects.new(cd2.name,cd2); kit.objects.link(cam2)
t2=c0+h*(whc+4.0)+Vector((0,0,gtop+1.2-c0.z))
l2=t2+out*9.0+h*3.0; ok,loc,_,_,_,_=sc.ray_cast(dg,Vector((l2.x,l2.y,170)),Vector((0,0,-1)))
cam2.location=(l2.x,l2.y,(loc.z if ok else gtop)+1.65); cd2.lens=28
cam2.rotation_euler=(t2-cam2.location).to_track_quat('-Z','Y').to_euler()
print('CAMS',cam.location[:],cam2.location[:])
bpy.ops.wm.save_mainfile(); print('SAVED')
