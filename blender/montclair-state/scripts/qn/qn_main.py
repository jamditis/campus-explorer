# qn: (1) QM underlay UV layer 'UVMap' -> 'ortho' so Ground_ortho_grass's UV Map node (uv_map='ortho') finds it (it read (0,0) =
# one flat ortho pixel -> flat/blurry patches on the CELS east lawn); (2) grass clump scatter on the lawn E/SE of CELS (box x 108-172,
# y 148-206, 6 m smoothstep fade at the box edge) instanced by the existing cx_grass_instancer. ALL UNVERIFIED (no photo of this lawn).
# REVERT=1 -> exact pre-qn state (layer name back, collection removed).
import bpy, os, sys, random, math
from mathutils import Vector
COL='QN_cels_east_lawn_grass_20261102qn'; OBN='QN_cels_east_lawn_grass_points_UNVERIFIED'
UN='QM_terrain_band_underlay_UNVERIFIED'
X0,X1,Y0,Y1,FADE=108.,172.,148.,206.,6.0
D=float(os.environ.get('D','22')); SEED=int(os.environ.get('SEED','1102'))
def revert():
  c=bpy.data.collections.get(COL)
  if c:
    for o in list(c.objects): bpy.data.objects.remove(o)
    bpy.data.collections.remove(c)
  for me in [m for m in bpy.data.meshes if m.name.startswith(OBN) and m.users==0]: bpy.data.meshes.remove(me)
  u=bpy.data.objects[UN]
  if u.get('qn_uv_prev'):
    u.data.uv_layers['ortho'].name=u['qn_uv_prev']; del u['qn_uv_prev']
  print("REVERTED")
revert()
if os.environ.get('REVERT')!='1':
  u=bpy.data.objects[UN]; L=u.data.uv_layers.active
  if L.name!='ortho': u['qn_uv_prev']=L.name; L.name='ortho'
  print('QN_UV layer',u.data.uv_layers.active.name)
  rnd=random.Random(SEED); dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
  okn={'Terrain_LiDAR_DTM_1m',UN,'QJ_NE_seam_fill_UNVERIFIED'}
  T=bpy.data.objects['Terrain_LiDAR_DTM_1m']
  okmat={'Ground_ortho_grass','Lawn_Varied_Oct_local_fade','COLE_lawn_post2020_bs'}
  def sm(t): t=min(max(t,0),1); return t*t*(3-2*t)
  pts=[]; nb=0; nm=0; nt=0
  gnd=[bpy.data.objects[n].evaluated_get(dg) for n in okn if n in bpy.data.objects]
  # blockers: every visible mesh whose world bbox overlaps the box (buildings, walks, roads, walls), except ground and plants
  blk=[]
  for o in sc.objects:
    if o.type!='MESH' or o.name in okn or o.hide_render or not o.visible_get(): continue
    nl=o.name.lower()
    if any(k in nl for k in ('grass','tree','shrub','skirt_3dep','farfield','helper','probe','patch','pc_','cx_')): continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    bx0=min(v.x for v in bb); bx1=max(v.x for v in bb); by0=min(v.y for v in bb); by1=max(v.y for v in bb)
    if bx1<X0 or bx0>X1 or by1<Y0 or by0>Y1: continue
    if (bx1-bx0)*(by1-by0)>4e5: continue
    blk.append((o.evaluated_get(dg),o.matrix_world.inverted(),bx0,bx1,by0,by1))
  print('QN blockers',len(blk))
  N=int(D*(X1-X0)*(Y1-Y0))
  for _ in range(N):
    x=X0+rnd.random()*(X1-X0); y=Y0+rnd.random()*(Y1-Y0)
    f=sm(min(x-X0,X1-x,y-Y0,Y1-y)/FADE)
    if rnd.random()>f: continue
    nt+=1; best=None
    for e in gnd:
      r=e.ray_cast(Vector((x,y,260)),Vector((0,0,-1)))
      if r[0] and (best is None or r[1].z>best[1].z): best=(e,r[1],r[2],r[3])
    if best is None or best[2].z<0.6: nb+=1; continue
    e,loc,n,fi=best
    if e.material_slots and e.material_slots[e.data.polygons[fi].material_index].name not in okmat: nm+=1; continue
    hit=False
    for b,iw,bx0,bx1,by0,by1 in blk:
      if x<bx0 or x>bx1 or y<by0 or y>by1: continue
      o0=iw@Vector((x,y,loc.z+40)); o1=iw@Vector((x,y,loc.z-0.08)); d=(o1-o0)
      r=b.ray_cast(o0,d.normalized(),distance=d.length)
      if r[0]: hit=True; break
    if hit: nb+=1; continue
    pts.append((x,y,loc.z-0.005))
  me=bpy.data.meshes.new(OBN); me.from_pydata(pts,[],[])
  ob=bpy.data.objects.new(OBN,me); c=bpy.data.collections.new(COL); sc.collection.children.link(c); c.objects.link(ob)
  src=bpy.data.objects['cx_grass_points'].modifiers['cx_grass']
  m=ob.modifiers.new('cx_grass','NODES'); m.node_group=src.node_group
  ob['UNVERIFIED_qn']='qn: grass clumps on the lawn E/SE of CELS, box x %g-%g y %g-%g, D=%g SEED=%d'%(X0,X1,Y0,Y1,D,SEED)
  print("QN_GRASS pts",len(pts),"tested",nt,"blocked(obj/slope)",nb,"nonlawn",nm)
if '--save' in sys.argv: bpy.ops.wm.save_mainfile(); print("SAVED")
