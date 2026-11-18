import bpy, bmesh, json, math
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
from mathutils.bvhtree import BVHTree
D='/workspace/nj-scenes/montclair-state/scripts/ws5/'
P=json.load(open(D+'pieces.json')); C=P['C']; R=P['R']
rings=[[tuple(c) for c in r] for r in P['union']['coordinates']]
def pin(x,y,r):
  ins=False; n=len(r); j=n-1
  for i in range(n):
    xi,yi=r[i]; xj,yj=r[j]
    if (yi>y)!=(yj>y) and x<(xj-xi)*(y-yi)/(yj-yi+1e-12)+xi: ins=not ins
    j=i
  return ins
BB=(-120,-96,-66,-40)
def inU(x,y):
  if not (BB[0]<x<BB[1] and BB[2]<y<BB[3]): return False
  return pin(x,y,rings[0])
sc=bpy.context.scene
T=bpy.data.objects['Terrain_LiDAR_DTM_1m']
tmp=bpy.data.scenes.new('ws5_tmp'); tmp.collection.objects.link(T)
with bpy.context.temp_override(scene=tmp,view_layer=tmp.view_layers[0]):
  dg=bpy.context.evaluated_depsgraph_get()
  oe=T.evaluated_get(dg); me=oe.to_mesh(); mw=T.matrix_world
  vs=[mw@v.co for v in me.vertices]; ps=[]
  for f in me.polygons:
    c=mw@f.center
    if -140<c.x<-60 and -90<c.y<-25: ps.append(list(f.vertices))
  TB=BVHTree.FromPolygons(vs,ps); oe.to_mesh_clear()
bpy.data.scenes.remove(tmp)
def tz(x,y):
  h=TB.ray_cast(Vector((x,y,300)),Vector((0,0,-1))); return h[0].z if h[0] else None
# existing WS3 paving height (to sit just above it where walks meet)
W=bpy.data.objects['WS3_Cole_plaza_paving_20261109']
wv=[W.matrix_world@v.co for v in W.data.vertices]
WB=BVHTree.FromPolygons(wv,[list(f.vertices) for f in W.data.polygons])
def wz(x,y):
  h=WB.ray_cast(Vector((x,y,300)),Vector((0,0,-1))); return h[0].z if h[0] else None
# --- 1. delete WS3 faces fully inside the new plaza; old disc brick -> concrete
bm=bmesh.new(); bm.from_mesh(W.data); mw=W.matrix_world
dl=[f for f in bm.faces if all(inU(*(mw@v.co).xy) for v in f.verts)]
bmesh.ops.delete(bm,geom=dl,context='FACES')
nb=0
for f in bm.faces:
  if f.material_index in (1,2): f.material_index=0; nb+=1
bm.to_mesh(W.data); bm.free(); print('WS3 del',len(dl),'brick->conc',nb)
def del_faces_in(n):
  o=bpy.data.objects.get(n)
  if not o: print('MISSING',n); return
  mw=o.matrix_world; bm=bmesh.new(); bm.from_mesh(o.data)
  fs=[f for f in bm.faces if inU(*(mw@f.calc_center_median()).xy)]
  bmesh.ops.delete(bm,geom=fs,context='FACES'); bm.to_mesh(o.data); bm.free(); print('del faces',n,len(fs))
def del_verts_in(n):
  o=bpy.data.objects.get(n)
  if not o: print('MISSING',n); return
  mw=o.matrix_world; bm=bmesh.new(); bm.from_mesh(o.data)
  vs=[v for v in bm.verts if inU(*(mw@v.co).xy)]
  bmesh.ops.delete(bm,geom=vs,context='VERTS'); bm.to_mesh(o.data); bm.free(); print('del verts',n,len(vs))
for n in ['Footpath control + expansion joints (3h)','Lawn_worn_edge_along_walks','cx_walk_joints_main','COLE_planting_beds_smooth_bu']: del_faces_in(n)
for n in ['cx_grass_points','Lawn_grass_instanced (3g)','cx_grass_fill_points']: del_verts_in(n)
# --- 2. retire lamp + bench that stood inside the new plaza
rc=bpy.data.collections.new('WS5_retired_20261109'); sc.collection.children.link(rc)
for n in ['Lamp_acorn_015','Bench_walk_016']:
  o=bpy.data.objects[n]
  for c in list(o.users_collection): c.objects.unlink(o)
  rc.objects.link(o)
  for ch in o.children_recursive:
    for c in list(ch.users_collection): c.objects.unlink(ch)
    rc.objects.link(ch)
rc.hide_render=True; rc.hide_viewport=True
for vl in sc.view_layers:
  lc=vl.layer_collection.children.get(rc.name)
  if lc: lc.exclude=True
# --- 3. materials
def mat_charcoal():
  m=bpy.data.materials.new('WS5_Charcoal_pavers_plaza'); m.use_nodes=True; nt=m.node_tree; N=nt.nodes; L=nt.links
  b=N['Principled BSDF']; geo=N.new('ShaderNodeNewGeometry'); sep=N.new('ShaderNodeSeparateXYZ'); L.new(geo.outputs['Position'],sep.inputs[0])
  js=[]
  for ax in ('X','Y'):
    pp=N.new('ShaderNodeMath'); pp.operation='PINGPONG'; pp.inputs[1].default_value=0.3; L.new(sep.outputs[ax],pp.inputs[0])
    lt=N.new('ShaderNodeMath'); lt.operation='LESS_THAN'; lt.inputs[1].default_value=0.006; L.new(pp.outputs[0],lt.inputs[0]); js.append(lt)
  jm=N.new('ShaderNodeMath'); jm.operation='MAXIMUM'; L.new(js[0].outputs[0],jm.inputs[0]); L.new(js[1].outputs[0],jm.inputs[1])
  nz=N.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value=2.2; nz.inputs['Detail'].default_value=8; L.new(geo.outputs['Position'],nz.inputs['Vector'])
  vo=N.new('ShaderNodeTexVoronoi'); vo.inputs['Scale'].default_value=3.33; L.new(geo.outputs['Position'],vo.inputs['Vector'])
  mx=N.new('ShaderNodeMath'); mx.operation='MULTIPLY_ADD'; mx.inputs[1].default_value=0.35; L.new(vo.outputs['Distance'],mx.inputs[0]); L.new(nz.outputs['Fac'],mx.inputs[2])
  ramp=N.new('ShaderNodeValToRGB'); ramp.color_ramp.elements[0].color=(0.060,0.060,0.064,1); ramp.color_ramp.elements[1].color=(0.135,0.133,0.135,1)
  L.new(mx.outputs[0],ramp.inputs[0])
  mix=N.new('ShaderNodeMix'); mix.data_type='RGBA'; mix.inputs['B'].default_value=(0.035,0.035,0.037,1)
  L.new(jm.outputs[0],mix.inputs['Factor']); L.new(ramp.outputs[0],mix.inputs['A']); L.new(mix.outputs['Result'],b.inputs['Base Color'])
  b.inputs['Roughness'].default_value=0.78
  bump=N.new('ShaderNodeBump'); bump.inputs['Strength'].default_value=0.5; bump.inputs['Distance'].default_value=0.003
  inv=N.new('ShaderNodeMath'); inv.operation='SUBTRACT'; inv.inputs[0].default_value=1; L.new(jm.outputs[0],inv.inputs[1])
  L.new(inv.outputs[0],bump.inputs['Height']); L.new(bump.outputs[0],b.inputs['Normal']); return m
def mat_stone():
  m=bpy.data.materials.new('WS5_Quatrefoil_inlay_light_stone'); m.use_nodes=True; nt=m.node_tree; N=nt.nodes; L=nt.links
  b=N['Principled BSDF']; geo=N.new('ShaderNodeNewGeometry')
  nz=N.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value=6; nz.inputs['Detail'].default_value=6; L.new(geo.outputs['Position'],nz.inputs['Vector'])
  ramp=N.new('ShaderNodeValToRGB'); ramp.color_ramp.elements[0].color=(0.58,0.57,0.54,1); ramp.color_ramp.elements[1].color=(0.74,0.73,0.70,1)
  L.new(nz.outputs['Fac'],ramp.inputs[0]); L.new(ramp.outputs[0],b.inputs['Base Color']); b.inputs['Roughness'].default_value=0.62; return m
mc=mat_charcoal(); mb=bpy.data.materials['WS3_Brick_pavers_running_bond']; ms=mat_stone()
# --- 4. plaza mesh
bm=bmesh.new()
for pc in P['pieces']:
  loops=[pc['ext']]+pc['holes']
  tris=tessellate_polygon([[Vector((x,y,0)) for (x,y) in lp] for lp in loops])
  vs=[bm.verts.new((x,y,0)) for lp in loops for (x,y) in lp]
  for t in tris:
    try: f=bm.faces.new([vs[t[0]],vs[t[1]],vs[t[2]]]); f.material_index=pc['m']
    except ValueError: pass
bmesh.ops.remove_doubles(bm,verts=bm.verts,dist=0.002)
miss=0
for v in bm.verts:
  z=tz(v.co.x,v.co.y)
  if z is None: miss+=1; z=134.2
  w=wz(v.co.x,v.co.y)
  v.co.z=max(z+0.065, (w+0.012) if w is not None else -1e9)
for f in bm.faces:
  if f.normal.z<0: f.normal_flip()
# light smoothing of z so the disc reads as one plane, not LiDAR noise
for it in range(3):
  nz={v:sum(e.other_vert(v).co.z for e in v.link_edges)/max(1,len(v.link_edges)) for v in bm.verts}
  for v,z in nz.items(): v.co.z=0.5*v.co.z+0.5*max(z,tz(v.co.x,v.co.y) or z)
me=bpy.data.meshes.new('WS5_Cole_plaza_circle'); bm.to_mesh(me); bm.free()
for m in (mc,mb,ms): me.materials.append(m)
o=bpy.data.objects.new('WS5_Cole_plaza_circle_quatrefoil_20261109',me)
pcol=bpy.data.collections.new('WS5_Cole_plaza_circle_20261109'); sc.collection.children.link(pcol); pcol.objects.link(o)
so=o.modifiers.new('WS5_skirt','SOLIDIFY'); so.thickness=0.2; so.offset=-1; so.use_rim=True
print('plaza faces',len(me.polygons),'miss',miss)
# --- 5. extended entrance roof -> same red clay tile as the main Cole roof
TZ=bpy.data.objects['TZ_Cole_north_addition_UNVERIFIED']; red=bpy.data.materials['Roof_tile_or_membrane']
for i,s in enumerate(TZ.material_slots):
  if s.material and s.material.name=='TZ_Cole_add_roof_UNVERIFIED':
    s.link='OBJECT' if s.link=='OBJECT' else s.link; s.material=red; print('roof slot',i,'->',red.name)
print('TZ rot',[round(x,3) for x in TZ.rotation_euler])
# --- 6. move the wayfinding sign: right-hand (Cole/south) edge of the walk heading east from the plaza, perpendicular to the walk
sign=bpy.data.objects['WS4_Sign_Wayfinding_ColeHall_UNVERIFIED_POS']
sx=-93.3; ys=[y/20 for y in range(-1000,-1240,-1)]  # y -50 .. -62
inside=[y for y in ys if wz(sx,y) is not None]
edge=min(inside) if inside else -55.0
# keep contiguous from the walk centre
print('walk hits at x',sx,'min',edge,'max',max(inside) if inside else None)
ny=edge-0.85
BED=bpy.data.objects['COLE_planting_beds_smooth_bu']; bv=[BED.matrix_world@v.co for v in BED.data.vertices]
BB2=BVHTree.FromPolygons(bv,[list(f.vertices) for f in BED.data.polygons])
h=BB2.ray_cast(Vector((sx,ny,300)),Vector((0,0,-1))); gz=h[0].z if h[0] else tz(sx,ny)
oz=tz(sign.location.x,sign.location.y); dz=sign.location.z-oz
print('sign old',[round(x,2) for x in sign.location],'rot',round(sign.rotation_euler.z,3),'dims',[round(x,2) for x in sign.dimensions],'old ground',round(oz,2),'dz',round(dz,3),'children',[c.name for c in sign.children])
sign.location=(sx,ny,gz+dz-0.01); sign.rotation_euler.z=-math.pi/2
print('sign new',[round(x,2) for x in sign.location])
import sys; sys.path.insert(0,D); import cams; cams.ensure(sc)
bpy.ops.wm.save_mainfile(); print('SAVED')
