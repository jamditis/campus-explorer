import bpy, math
from mathutils import Vector
sc=bpy.context.scene
# ---------- (a) walk retone: all Footpaths_OSM faces -> WS3 concrete tone without grid joints (3h joints already follow the walks)
F=bpy.data.objects['Footpaths_OSM']
old=F.material_slots[0].material; old.use_fake_user=True
src=bpy.data.materials['WS3_Concrete_panels_sawcut']
m=src.copy(); m.name='WS4_Concrete_walk_broom_nogrid'
for n in m.node_tree.nodes:
  if n.bl_idname=='ShaderNodeMath' and n.operation=='LESS_THAN': n.inputs[1].default_value=-1.0  # disables the 1.8 m world grid joints
F.material_slots[0].material=m
print('RETONE',old.name,'->',m.name,'faces',sum(1 for p in F.data.polygons if p.material_index==0))
# ---------- (b) Cole walk kit
KIT='/workspace/nj-scenes/assets/cole_walk_kit_wr3.blend'
names=['Sign_Wayfinding_ColeHall_wr3','Lamp_Post_Globe_ColeWalk_wr3','Bed_RiverRock_Strip_wr3']
with bpy.data.libraries.load(KIT,link=False) as (src_,dst):
  dst.collections=[n for n in names if n in src_.collections]
srcc=bpy.data.collections.new('WS4_kit_sources_20261109'); sc.collection.children.link(srcc)
for c in dst.collections: srcc.children.link(c)
lc=bpy.context.view_layer.layer_collection.children[srcc.name]; lc.exclude=True
for o in bpy.data.objects:
  if o.name.startswith('GlobeLamp_globe_wr3'):
    for s in o.material_slots:
      if s.material and s.material.use_nodes:
        b=s.material.node_tree.nodes.get('Principled BSDF')
        if b: b.inputs['Emission Strength'].default_value=4.0
pc=bpy.data.collections.new('WS4_Cole_walk_kit_20261109'); sc.collection.children.link(pc)
mw=F.matrix_world; V=[mw@v.co for v in F.data.vertices]
def north_edge(x,ylo=-62,yhi=-47):
  ys=[(v.y,v.z) for v in V if abs(v.x-x)<0.8 and ylo<v.y<yhi]
  if not ys: return None
  y,z=max(ys); return y,z
def inst(cname,loc,rotz,label):
  e=bpy.data.objects.new(label,None); e.instance_type='COLLECTION'; e.instance_collection=bpy.data.collections[cname]
  e.location=loc; e.rotation_euler=(0,0,rotz); pc.objects.link(e); return e
placed=[]
# sign near Cole's NE, facing the walk (south); lamps every ~15 m on the walk's north edge toward Morehead
ne=north_edge(-72)
print('SIGN EDGE',ne)
if ne:
  y,z=ne; s=inst('Sign_Wayfinding_ColeHall_wr3',(-72,y+1.1,z-0.08),0,'WS4_Sign_Wayfinding_ColeHall_UNVERIFIED_POS'); placed.append(s.name)
  r=inst('Bed_RiverRock_Strip_wr3',(-72,y+0.45,z-0.06),0,'WS4_RiverRock_strip_sign_bed_UNVERIFIED_POS'); placed.append(r.name)
for x in (-80,-64,-50):
  ne=north_edge(x)
  print('LAMP EDGE',x,ne)
  if ne:
    y,z=ne; l=inst('Lamp_Post_Globe_ColeWalk_wr3',(x,y+0.7,z-0.1),0,f'WS4_Globe_lamp_x{abs(x)}_UNVERIFIED_POS'); placed.append(l.name)
print('PLACED',placed)
# camera close-up on the sign
sgn=bpy.data.objects.get('WS4_Sign_Wayfinding_ColeHall_UNVERIFIED_POS')
if sgn:
  t=sgn.location+Vector((0,0,1.3)); cp=sgn.location+Vector((-3.5,-7.0,1.65))
  cd=bpy.data.cameras.new('WS4_CAM_closeup_cole_sign'); cd.lens=35
  co=bpy.data.objects.new('WS4_CAM_closeup_cole_sign_from_SW',cd); co.location=cp
  co.rotation_euler=(t-cp).to_track_quat('-Z','Y').to_euler(); pc.objects.link(co)
bpy.ops.wm.save_mainfile()
print('SAVED')
