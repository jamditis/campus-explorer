import bpy, bmesh, json, math
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree
D='/workspace/nj-scenes/montclair-state/scripts/ws3/'
P=json.load(open(D+'pieces.json')); E=json.load(open(D+'extract.json'))
R=E['R']; RE=(R[0]-6,R[1]+6,R[2]-6,R[3]+6)
U=P['union']; assert U['type']=='Polygon'
rings=[[tuple(c) for c in r] for r in U['coordinates']]
def pin_ring(x,y,r):
  ins=False; n=len(r); j=n-1
  for i in range(n):
    xi,yi=r[i]; xj,yj=r[j]
    if (yi>y)!=(yj>y) and x<(xj-xi)*(y-yi)/(yj-yi+1e-12)+xi: ins=not ins
    j=i
  return ins
def inU(x,y):
  if not (R[0]-2<x<R[1]+2 and R[2]-2<y<R[3]+2): return False
  return pin_ring(x,y,rings[0]) and not any(pin_ring(x,y,h) for h in rings[1:])
sc=bpy.context.scene
T=bpy.data.objects['Terrain_LiDAR_DTM_1m']; F=bpy.data.objects['Footpaths_OSM']
# --- evaluate only terrain + footpaths in a temp scene
tmp=bpy.data.scenes.new('ws3_tmp'); tmp.collection.objects.link(T); tmp.collection.objects.link(F)
with bpy.context.temp_override(scene=tmp,view_layer=tmp.view_layers[0]):
  dg=bpy.context.evaluated_depsgraph_get()
print('DG objs',len([1 for _ in dg.object_instances]))
def region_bvh(o):
  oe=o.evaluated_get(dg); me=oe.to_mesh(); mw=o.matrix_world
  vs=[mw@v.co for v in me.vertices]; ps=[]
  for f in me.polygons:
    c=mw@f.center
    if RE[0]<c.x<RE[1] and RE[2]<c.y<RE[3]: ps.append(list(f.vertices))
  b=BVHTree.FromPolygons(vs,ps); n=len(me.vertices); nf=len(me.polygons)
  oe.to_mesh_clear(); return b,vs,n,nf
TB,_,_,_=region_bvh(T)
FB,FV,fn,ffn=region_bvh(F)
print('FOOT eval verts',fn,'base',len(F.data.vertices),'faces',ffn,len(F.data.polygons))
def tz(x,y):
  h=TB.ray_cast(Vector((x,y,300)),Vector((0,0,-1)))
  return h[0].z if h[0] else None
# kept footpath verts (for seam snapping) — eval positions, if topology matches
deleted=set(P['deleted_faces'])
kd=None
if fn==len(F.data.vertices):
  used=set()
  for f in F.data.polygons:
    if f.index not in deleted: used.update(f.vertices)
  pts=[(i,FV[i]) for i in used if RE[0]<FV[i].x<RE[1] and RE[2]<FV[i].y<RE[3]]
  kd=KDTree(len(pts))
  for k,(i,p) in enumerate(pts): kd.insert(p,k)
  kd.balance(); kpts=pts
bpy.data.scenes.remove(tmp)
# --- delete footpath faces in region
bm=bmesh.new(); bm.from_mesh(F.data); bm.faces.ensure_lookup_table()
bmesh.ops.delete(bm,geom=[bm.faces[i] for i in deleted],context='FACES_ONLY')
loose=[v for v in bm.verts if not v.link_faces]; bmesh.ops.delete(bm,geom=loose,context='VERTS')
bm.to_mesh(F.data); bm.free(); print('deleted walk faces',len(deleted))
def del_faces_in(o,pad=0.0):
  mw=o.matrix_world; bm=bmesh.new(); bm.from_mesh(o.data)
  fs=[f for f in bm.faces if (lambda c: inU(c.x,c.y))(mw@f.calc_center_median())]
  bmesh.ops.delete(bm,geom=fs,context='FACES'); bm.to_mesh(o.data); bm.free(); print('del faces',o.name,len(fs))
def del_verts_in(o):
  mw=o.matrix_world; bm=bmesh.new(); bm.from_mesh(o.data)
  vs=[v for v in bm.verts if (lambda p: inU(p.x,p.y))(mw@v.co)]
  bmesh.ops.delete(bm,geom=vs,context='VERTS'); bm.to_mesh(o.data); bm.free(); print('del verts',o.name,len(vs))
del_faces_in(bpy.data.objects['Footpath control + expansion joints (3h)'])
del_faces_in(bpy.data.objects['Lawn_worn_edge_along_walks'])
del_verts_in(bpy.data.objects['cx_grass_points'])
del_verts_in(bpy.data.objects['Lawn_grass_instanced (3g)'])
# --- retire the striped disc
disc=bpy.data.objects['COLE_add_forecourt_bu']
rc=bpy.data.collections.get('WS3_retired_20261109') or bpy.data.collections.new('WS3_retired_20261109')
if rc.name not in sc.collection.children: sc.collection.children.link(rc)
for c in list(disc.users_collection): c.objects.unlink(disc)
rc.objects.link(disc); rc.hide_render=True; rc.hide_viewport=True
# --- materials
def mat_concrete():
  m=bpy.data.materials.new('WS3_Concrete_panels_sawcut'); m.use_nodes=True; nt=m.node_tree; N=nt.nodes; L=nt.links
  b=N['Principled BSDF']; geo=N.new('ShaderNodeNewGeometry')
  sep=N.new('ShaderNodeSeparateXYZ'); L.new(geo.outputs['Position'],sep.inputs[0])
  def joint(axis,period,width=0.012):
    mth=N.new('ShaderNodeMath'); mth.operation='PINGPONG'; mth.inputs[1].default_value=period/2
    L.new(sep.outputs[axis],mth.inputs[0])
    st=N.new('ShaderNodeMath'); st.operation='LESS_THAN'; st.inputs[1].default_value=width; L.new(mth.outputs[0],st.inputs[0]); return st
    # pingpong(x, p/2) = distance to nearest multiple of p -> near 0 at the joints
  jx=joint('X',1.8); jy=joint('Y',1.8)
  jm=N.new('ShaderNodeMath'); jm.operation='MAXIMUM'; L.new(jx.outputs[0],jm.inputs[0]); L.new(jy.outputs[0],jm.inputs[1])
  nz=N.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value=1.6; nz.inputs['Detail'].default_value=8
  L.new(geo.outputs['Position'],nz.inputs['Vector'])
  ramp=N.new('ShaderNodeValToRGB'); ramp.color_ramp.elements[0].color=(0.44,0.43,0.40,1); ramp.color_ramp.elements[1].color=(0.58,0.57,0.53,1)
  L.new(nz.outputs['Fac'],ramp.inputs[0])
  mix=N.new('ShaderNodeMix'); mix.data_type='RGBA'; mix.inputs['B'].default_value=(0.22,0.21,0.2,1)
  L.new(jm.outputs[0],mix.inputs['Factor']); L.new(ramp.outputs[0],mix.inputs['A']); L.new(mix.outputs['Result'],b.inputs['Base Color'])
  b.inputs['Roughness'].default_value=0.88
  bump=N.new('ShaderNodeBump'); bump.inputs['Strength'].default_value=0.6; bump.inputs['Distance'].default_value=0.004
  inv=N.new('ShaderNodeMath'); inv.operation='SUBTRACT'; inv.inputs[0].default_value=1; L.new(jm.outputs[0],inv.inputs[1])
  fn=N.new('ShaderNodeTexNoise'); fn.inputs['Scale'].default_value=180
  L.new(geo.outputs['Position'],fn.inputs['Vector'])
  add=N.new('ShaderNodeMath'); add.operation='MULTIPLY_ADD'; add.inputs[1].default_value=0.15
  L.new(fn.outputs['Fac'],add.inputs[0]); L.new(inv.outputs[0],add.inputs[2])
  L.new(add.outputs[0],bump.inputs['Height']); L.new(bump.outputs[0],b.inputs['Normal'])
  return m
def mat_brick(name,c1,c2,scale,bw,rh):
  m=bpy.data.materials.new(name); m.use_nodes=True; nt=m.node_tree; N=nt.nodes; L=nt.links
  b=N['Principled BSDF']; geo=N.new('ShaderNodeNewGeometry')
  br=N.new('ShaderNodeTexBrick'); br.offset=0.5
  br.inputs['Color1'].default_value=c1; br.inputs['Color2'].default_value=c2
  br.inputs['Mortar'].default_value=(0.42,0.40,0.37,1); br.inputs['Scale'].default_value=scale
  br.inputs['Mortar Size'].default_value=0.008; br.inputs['Brick Width'].default_value=bw; br.inputs['Row Height'].default_value=rh
  br.inputs['Bias'].default_value=0.0
  L.new(geo.outputs['Position'],br.inputs['Vector']); L.new(br.outputs['Color'],b.inputs['Base Color'])
  b.inputs['Roughness'].default_value=0.82
  bump=N.new('ShaderNodeBump'); bump.inputs['Strength'].default_value=0.5; bump.inputs['Distance'].default_value=0.006
  L.new(br.outputs['Fac'],bump.inputs['Height']); L.new(bump.outputs[0],b.inputs['Normal'])
  return m
mc=mat_concrete()
mb=mat_brick('WS3_Brick_pavers_running_bond',(0.34,0.09,0.05,1),(0.52,0.32,0.18,1),1.0,0.20,0.10)
ms=mat_brick('WS3_Brick_soldier_course',(0.36,0.11,0.06,1),(0.46,0.18,0.10,1),1.0,0.10,0.20)
# --- build paving mesh
bm=bmesh.new(); cnt=0
for pc in P['pieces']:
  loops=[pc['ext']]+pc['holes']
  vl=[Vector((x,y,0)) for lp in loops for (x,y) in lp]
  tris=tessellate_polygon([[Vector((x,y,0)) for (x,y) in lp] for lp in loops])
  vs=[bm.verts.new(v) for v in vl]
  for t in tris:
    try:
      f=bm.faces.new([vs[t[0]],vs[t[1]],vs[t[2]]]); f.material_index=pc['m']; cnt+=1
    except ValueError: pass
bmesh.ops.remove_doubles(bm,verts=bm.verts,dist=0.002)
miss=0; snapped=0
for v in bm.verts:
  z=tz(v.co.x,v.co.y)
  if z is None: miss+=1; z=134.0
  v.co.z=z+0.05
  if kd:
    p,k,d=kd.find(Vector((v.co.x,v.co.y,v.co.z)))
    q=kpts[k][1]
    if (Vector((q.x,q.y))-Vector((v.co.x,v.co.y))).length<0.04: v.co.z=max(q.z,z+0.02); snapped+=1
for f in bm.faces:
  if f.normal.z<0: f.normal_flip()
me=bpy.data.meshes.new('WS3_Cole_plaza_paving'); bm.to_mesh(me); bm.free()
for m in (mc,mb,ms): me.materials.append(m)
for p in me.polygons: p.use_smooth=False
o=bpy.data.objects.new('WS3_Cole_plaza_paving_20261109',me)
pc=bpy.data.collections.get('WS3_Cole_plaza_20261109') or bpy.data.collections.new('WS3_Cole_plaza_20261109')
if pc.name not in sc.collection.children: sc.collection.children.link(pc)
pc.objects.link(o)
so=o.modifiers.new('WS3_skirt','SOLIDIFY'); so.thickness=0.18; so.offset=-1; so.use_rim=True
print('PAVING tris',cnt,'verts',len(me.vertices),'miss',miss,'snapped',snapped)
# --- cameras
def cam(name,loc,tgt,lens):
  c=bpy.data.cameras.new(name); c.lens=lens; c.clip_start=0.1; c.clip_end=20000
  ob=bpy.data.objects.new(name,c); pc.objects.link(ob); ob.location=loc
  ob.rotation_euler=(Vector(tgt)-Vector(loc)).to_track_quat('-Z','Y').to_euler(); return ob
cx,cy=-107.5,-46.4
z0=tz(-124,-60) or 134.0
cam('WS3_CAM_eye_cole_plaza_from_SW',(-124,-60,z0+1.65),(cx,cy,(tz(cx,cy) or 134)+1.0),28)
cam('WS3_CAM_closeup_cole_plaza_from_NW',(-124,-33,143.0),(-107,-47,134.2),30)
import os
bpy.ops.wm.save_mainfile()
print('SAVED',bpy.data.filepath)
