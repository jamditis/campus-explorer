import bpy, os, resource
from mathutils import Vector
P='/workspace/nj-scenes/montclair-state/montclair_state.blend'
TAG=os.environ.get('TAG','a'); DEL=os.environ.get('DEL','')
want=['T_RedMaple_L1_0158','WS142_Lot9_asphalt_OSM312845867_LiDAR2023int_ortho2020_UNVERIFI','WS143_Freeman_NE_forecourt_concrete_LiDAR2023int_ortho2020_UNVE','WS143_Freeman_NE_forecourt_curb_LiDAR2023step0p10_UNVERIFIEDsec']
with bpy.data.libraries.load(P, link=False) as (src,dst):
    dst.objects=list(want)
sc=bpy.context.scene
for n in ('Cube',):
    if n in bpy.data.objects: bpy.data.objects.remove(bpy.data.objects[n])
for o in dst.objects:
    for m in list(o.modifiers): o.modifiers.remove(m)
    if o.name not in sc.collection.objects: sc.collection.objects.link(o)
t=bpy.data.objects['T_RedMaple_L1_0158']
print("TREE loc",tuple(round(v,2) for v in t.matrix_world.translation),"users",t.data.users,"mesh",t.data.name,"faces",len(t.data.polygons))
base=t.matrix_world.translation.z
cam=bpy.data.objects['Camera']
loc=Vector((-64.5,-160,129.9+1.7)); tgt=Vector((-73,-176,128.6+0.5))
cam.location=loc; cam.data.lens=26; cam.data.clip_start=0.1
cam.rotation_euler=(tgt-loc).to_track_quat('-Z','Y').to_euler(); sc.camera=cam
dg=bpy.context.evaluated_depsgraph_get()
# cast grid of rays through the frame, record leaf face hits
import mathutils
me=t.data; leafidx=[i for i,s in enumerate(t.material_slots) if s.material and 'Leaf' in s.material.name]
hits={}
fr=cam.data.view_frame(scene=sc); mw=cam.matrix_world
for iy in range(0,36):
  for ix in range(0,64):
    u=ix/63; v=iy/35
    p=fr[2].lerp(fr[1],u); q=fr[3].lerp(fr[0],u); d=(mw@(p.lerp(q,v)))-mw.translation
    ok,lp,n,fi,ob,_=sc.ray_cast(dg,mw.translation,d.normalized())
    if ok and ob.name==t.name:
        hits[fi]=hits.get(fi,0)+1
print("LEAFHITS",len(hits),sorted(hits.items(),key=lambda k:-k[1])[:20])
for fi in list(hits)[:10]:
    pp=me.polygons[fi]; c=t.matrix_world@pp.center; print('  radial',round(pp.center.xy.length,2))
    print(" face",fi,"mat",pp.material_index,"world",tuple(round(x,2) for x in c),"localz",round(pp.center.z,2),"dist",round((c-loc).length,2))
# local z distribution of leaf faces
zs=sorted(p.center.z for p in me.polygons if p.material_index in leafidx)
print("LEAF localz min",round(zs[0],2),"p5",round(zs[len(zs)//20],2),"n",len(zs))
if DEL:
    import bmesh
    bm=bmesh.new(); bm.from_mesh(me); bm.faces.ensure_lookup_table()
    kill=[f for f in bm.faces if f.material_index in leafidx and f.calc_center_median().z<float(DEL)]; print('KILLED',len(kill))
    if os.environ.get('DELB'):
        kb=[f for f in bm.faces if f.material_index not in leafidx and f.calc_center_median().z<float(DEL) and f.calc_center_median().xy.length>float(os.environ['DELB'])]; print('KILLB',len(kb)); kill+=kb
    bmesh.ops.delete(bm,geom=kill,context='FACES'); bm.to_mesh(me); bm.free()
sun=bpy.data.objects.new('S',bpy.data.lights.new('S','SUN')); sun.data.energy=3; sun.rotation_euler=(0.8,0.2,2.4); sc.collection.objects.link(sun)
sc.render.engine='CYCLES'; sc.cycles.device='CPU'; sc.cycles.samples=8; sc.render.resolution_x=640; sc.render.resolution_y=360
sc.render.image_settings.file_format='JPEG'
sc.render.filepath='/workspace/nj-scenes/montclair-state/scripts/ws148/prev148_%s.jpg'%TAG
bpy.ops.render.render(write_still=True); print("RSS",resource.getrusage(resource.RUSAGE_SELF).ru_maxrss//1024)
