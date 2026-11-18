# qo (Nov 2 2026, MAIN, day 7 CELS/CCIS). ALL UNVERIFIED, reversible: REVERT=1 -> exact pre-qo state.
# (1) repath image ortho2020_north.jpg.001 -> //north/data/ortho2020_north.jpg (prop on image keeps the old path)
# (2) pale washed-out ground W/SW of CELS: local tone mask in Ground_ortho_grass (world-position box x 40-92, y 150-218,
#     6 m fade, only where the 2020 ortho is pale: lum>0.42) pulls the base colour toward the grass texture/green;
#     + cx_grass clump points (qn method) in the same box.
# (3) CCIS podium roof edge east (x 29-38, y 204-224, z 140.5-141.25): LiDAR-roof dark fascia/soffit faces deleted
#     (they stuck out past the QF cornice as a dark wedge/spike) by GN QO_ccis_podium_lip_mat (last modifier, mesh unedited).
# (4) NE road/walk lift near (221,214.5): GN QO_NE_lift_drape (last on Roads_OSM/Footpaths_OSM) drops verts that sit
#     >0.02 m above (single centre ray ground + target) in small boxes to ground+target (roads +0.15 m so the terrain step
#     between verts stays under the asphalt; walks +0.05 m).
import bpy, os, sys, random, math
from mathutils import Vector
REV=os.environ.get('REVERT')=='1'
TAG='qo'
MAT='Ground_ortho_grass'
COL='QO_cels_west_lawn_grass_20261102qo'; OBN='QO_cels_west_lawn_grass_points_UNVERIFIED'
BX0,BX1,BY0,BY1,FADE=40.,92.,150.,218.,6.0
ROOF='Center for Computing and Information Science roof (LiDAR)'
def revert():
  im=bpy.data.images.get('ortho2020_north.jpg.001')
  if im and im.get('qo_prev_path'): im.filepath=im['qo_prev_path']; del im['qo_prev_path']
  nt=bpy.data.materials[MAT].node_tree
  for nd in [n for n in nt.nodes if n.name.startswith('QO_')]: nt.nodes.remove(nd)
  pb=nt.nodes['Principled BSDF']
  if not pb.inputs['Base Color'].is_linked: nt.links.new(nt.nodes['Mix.001'].outputs[2], pb.inputs['Base Color'])
  c=bpy.data.collections.get(COL)
  if c:
    for o in list(c.objects): bpy.data.objects.remove(o)
    bpy.data.collections.remove(c)
  for me in [m for m in bpy.data.meshes if m.name.startswith(OBN) and m.users==0]: bpy.data.meshes.remove(me)
  for on,mn in ((ROOF,'QO_ccis_podium_lip_mat'),('Roads_OSM','QO_NE_lift_drape'),('Footpaths_OSM','QO_NE_lift_drape'),('QJ_NE_seam_fill_UNVERIFIED','QO_fill_sink_under_road')):
    o=bpy.data.objects[on]; m=o.modifiers.get(mn)
    if m: o.modifiers.remove(m)
  for g in [g for g in bpy.data.node_groups if g.name.startswith('QO_')]: bpy.data.node_groups.remove(g)
  print('QO REVERTED')

def tone_mask():
  nt=bpy.data.materials[MAT].node_tree; N=nt.nodes; L=nt.links
  pb=N['Principled BSDF']; m1=N['Mix.001']; ortho=N['Image Texture.003']; grass=N['Image Texture']
  def nd(t,name,x,y):
    n=N.new(t); n.name=n.label=name; n.location=(x,y); return n
  geo=nd('ShaderNodeNewGeometry','QO_geo',-1400,-900)
  sep=nd('ShaderNodeSeparateXYZ','QO_sepxyz',-1200,-900); L.new(geo.outputs['Position'],sep.inputs[0])
  def edge(axis,lo,hi,y):
    # smoothstep fade inside [lo,hi] with FADE margin
    a=nd('ShaderNodeMapRange','QO_mr_%s_lo'%axis,-1000,y); a.interpolation_type='SMOOTHSTEP'
    a.inputs['From Min'].default_value=lo; a.inputs['From Max'].default_value=lo+FADE
    L.new(sep.outputs[axis],a.inputs['Value'])
    b=nd('ShaderNodeMapRange','QO_mr_%s_hi'%axis,-1000,y-200); b.interpolation_type='SMOOTHSTEP'
    b.inputs['From Min'].default_value=hi; b.inputs['From Max'].default_value=hi-FADE
    L.new(sep.outputs[axis],b.inputs['Value'])
    m=nd('ShaderNodeMath','QO_mul_%s'%axis,-800,y); m.operation='MULTIPLY'
    L.new(a.outputs[0],m.inputs[0]); L.new(b.outputs[0],m.inputs[1]); return m
  mx=edge('X',BX0,BX1,-900); my=edge('Y',BY0,BY1,-1300)
  box=nd('ShaderNodeMath','QO_box',-600,-1000); box.operation='MULTIPLY'; L.new(mx.outputs[0],box.inputs[0]); L.new(my.outputs[0],box.inputs[1])
  # paleness of the ortho: luminance via RGB->BW, map 0.42..0.62 -> 0..1
  bw=nd('ShaderNodeRGBToBW','QO_ortho_lum',-1000,-1700); L.new(ortho.outputs['Color'],bw.inputs[0])
  pm=nd('ShaderNodeMapRange','QO_pale',-800,-1700); pm.inputs['From Min'].default_value=float(os.environ.get('PL0','0.30')); pm.inputs['From Max'].default_value=float(os.environ.get('PL1','0.50'))
  L.new(bw.outputs[0],pm.inputs['Value'])
  f=nd('ShaderNodeMath','QO_fac',-400,-1200); f.operation='MULTIPLY'; L.new(box.outputs[0],f.inputs[0]); L.new(pm.outputs[0],f.inputs[1])
  fs=nd('ShaderNodeMath','QO_fac_strength',-250,-1200); fs.operation='MULTIPLY'; fs.inputs[1].default_value=float(os.environ.get('STR','0.85')); L.new(f.outputs[0],fs.inputs[0])
  hsv=nd('ShaderNodeHueSaturation','QO_lawn_hsv',-400,-600); L.new(grass.outputs['Color'],hsv.inputs['Color'])
  hsv.inputs['Hue'].default_value=0.5; hsv.inputs['Saturation'].default_value=0.9; hsv.inputs['Value'].default_value=float(os.environ.get('VAL','0.80'))
  # keep some ortho variation: lawn = mix(grass_hsv, ortho*greenTint, 0.25)
  tint=nd('ShaderNodeMix','QO_ortho_green',-400,-400); tint.data_type='RGBA'; tint.blend_type='MULTIPLY'; tint.inputs[0].default_value=1.0
  L.new(ortho.outputs['Color'],tint.inputs[6]); tint.inputs[7].default_value=(0.55,0.68,0.42,1)
  lawn=nd('ShaderNodeMix','QO_lawn',-200,-500); lawn.data_type='RGBA'; lawn.inputs[0].default_value=0.25
  L.new(hsv.outputs[0],lawn.inputs[6]); L.new(tint.outputs[2],lawn.inputs[7])
  out=nd('ShaderNodeMix','QO_tone_mix',0,-300); out.data_type='RGBA'
  L.new(fs.outputs[0],out.inputs[0]); L.new(m1.outputs[2],out.inputs[6]); L.new(lawn.outputs[2],out.inputs[7])
  L.new(out.outputs[2],pb.inputs['Base Color'])
  print('QO tone mask nodes',len([n for n in N if n.name.startswith('QO_')]))

def grass():
  D=float(os.environ.get('D','35')); SEED=int(os.environ.get('SEED','1103'))
  rnd=random.Random(SEED); dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
  okn={'Terrain_LiDAR_DTM_1m','QM_terrain_band_underlay_UNVERIFIED','QJ_NE_seam_fill_UNVERIFIED'}
  okmat={'Ground_ortho_grass','Lawn_Varied_Oct_local_fade','COLE_lawn_post2020_bs'}
  def sm(t): t=min(max(t,0),1); return t*t*(3-2*t)
  gnd=[bpy.data.objects[n].evaluated_get(dg) for n in okn if n in bpy.data.objects]
  blk=[]
  for o in sc.objects:
    if o.type!='MESH' or o.name in okn or o.hide_render or not o.visible_get(): continue
    nl=o.name.lower()
    if any(k in nl for k in ('grass','tree','shrub','skirt_3dep','farfield','helper','probe','patch','pc_','cx_')): continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    bx0=min(v.x for v in bb); bx1=max(v.x for v in bb); by0=min(v.y for v in bb); by1=max(v.y for v in bb)
    if bx1<BX0 or bx0>BX1 or by1<BY0 or by0>BY1: continue
    if (bx1-bx0)*(by1-by0)>4e5: continue
    blk.append((o.evaluated_get(dg),o.matrix_world.inverted(),bx0,bx1,by0,by1))
  print('QO blockers',len(blk))
  pts=[]; nb=nm=nt=0
  for _ in range(int(D*(BX1-BX0)*(BY1-BY0))):
    x=BX0+rnd.random()*(BX1-BX0); y=BY0+rnd.random()*(BY1-BY0)
    if rnd.random()>sm(min(x-BX0,BX1-x,y-BY0,BY1-y)/FADE): continue
    nt+=1; best=None
    for e in gnd:
      iw=e.matrix_world.inverted(); r=e.ray_cast(iw@Vector((x,y,260)),Vector((0,0,-1)))
      if r[0]:
        loc=e.matrix_world@r[1]
        if best is None or loc.z>best[1].z: best=(e,loc,r[2],r[3])
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
  m=ob.modifiers.new('cx_grass','NODES'); m.node_group=bpy.data.objects['cx_grass_points'].modifiers['cx_grass'].node_group
  ob['UNVERIFIED_qo']='qo: grass clumps on the pale lawn W/SW of CELS, box x %g-%g y %g-%g, D=%g SEED=%d'%(BX0,BX1,BY0,BY1,D,SEED)
  print('QO_GRASS pts',len(pts),'tested',nt,'blocked',nb,'nonlawn',nm)

def podium():
  o=bpy.data.objects[ROOF]
  mats=[s.material for s in o.material_slots]; names=[m.name if m else '' for m in mats]
  stucco=bpy.data.materials['QE_CCIS_stucco_no_shader_windows_UNVERIFIED']
  g=bpy.data.node_groups.new('QO_ccis_podium_lip_mat','GeometryNodeTree')
  g.interface.new_socket('Geometry',in_out='INPUT',socket_type='NodeSocketGeometry'); g.interface.new_socket('Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry')
  N=g.nodes; L=g.links; gi=N.new('NodeGroupInput'); go=N.new('NodeGroupOutput')
  pos=N.new('GeometryNodeInputPosition'); sep=N.new('ShaderNodeSeparateXYZ'); L.new(pos.outputs[0],sep.inputs[0])
  # face-domain position via Capture? Set Material selection is on faces; position field is evaluated per face (averaged) automatically.
  conds=[]
  for ax,lo,hi in (('X',29.0,38.0),('Y',204.0,224.0),('Z',140.5,141.25)):
    c=N.new('FunctionNodeCompare'); c.data_type='FLOAT'; c.operation='GREATER_THAN'; L.new(sep.outputs[ax],c.inputs[0]); c.inputs[1].default_value=lo
    d=N.new('FunctionNodeCompare'); d.data_type='FLOAT'; d.operation='LESS_THAN'; L.new(sep.outputs[ax],d.inputs[0]); d.inputs[1].default_value=hi
    conds+= [c.outputs[0],d.outputs[0]]
  ms=[]
  for nm in ('Eave_fascia_dark_wood','Eave_tile_top_soffit_under'):
    if nm in bpy.data.materials:
      s=N.new('GeometryNodeMaterialSelection'); s.inputs[0].default_value=bpy.data.materials[nm]; ms.append(s.outputs[0])
  orm=N.new('FunctionNodeBooleanMath'); orm.operation='OR'; L.new(ms[0],orm.inputs[0]); L.new(ms[1],orm.inputs[1]); conds.append(orm.outputs[0])
  acc=conds[0]
  for c in conds[1:]:
    a=N.new('FunctionNodeBooleanMath'); a.operation='AND'; L.new(acc,a.inputs[0]); L.new(c,a.inputs[1]); acc=a.outputs[0]
  sm=N.new('GeometryNodeDeleteGeometry'); sm.domain='FACE'
  L.new(gi.outputs[0],sm.inputs['Geometry']); L.new(acc,sm.inputs['Selection'])
  # clamp the folded tile spike at the S end of the podium edge (x 29.2-31.2, y 205.3-207.8) onto the flat roof plane z 141.09
  c2=[]
  for ax,lo,hi in (('X',29.2,31.2),('Y',205.3,207.8),('Z',141.095,141.8)):
    c=N.new('FunctionNodeCompare'); c.data_type='FLOAT'; c.operation='GREATER_THAN'; L.new(sep.outputs[ax],c.inputs[0]); c.inputs[1].default_value=lo
    d=N.new('FunctionNodeCompare'); d.data_type='FLOAT'; d.operation='LESS_THAN'; L.new(sep.outputs[ax],d.inputs[0]); d.inputs[1].default_value=hi
    c2+=[c.outputs[0],d.outputs[0]]
  a2=c2[0]
  for c in c2[1:]:
    a=N.new('FunctionNodeBooleanMath'); a.operation='AND'; L.new(a2,a.inputs[0]); L.new(c,a.inputs[1]); a2=a.outputs[0]
  cm=N.new('ShaderNodeCombineXYZ'); L.new(sep.outputs['X'],cm.inputs[0]); L.new(sep.outputs['Y'],cm.inputs[1]); cm.inputs[2].default_value=141.09
  sp=N.new('GeometryNodeSetPosition'); L.new(sm.outputs[0],sp.inputs['Geometry']); L.new(a2,sp.inputs['Selection']); L.new(cm.outputs[0],sp.inputs['Position'])
  L.new(sp.outputs[0],go.inputs[0])
  m=o.modifiers.new('QO_ccis_podium_lip_mat','NODES'); m.node_group=g
  o['UNVERIFIED_qo']='qo: dark LiDAR fascia/soffit faces at the CCIS east podium edge deleted (GN, mesh unedited)'
  print('QO podium GN added')

def lift():
  grounds=[bpy.data.objects[n] for n in ('Terrain_LiDAR_DTM_1m','QJ_NE_seam_fill_UNVERIFIED','Context_skirt_3DEP_ortho_4km')]
  for on,off,box in (('Roads_OSM',float(os.environ.get('ROAD_TGT','0.15')),(216.5,227.0,199.0,218.5)),('Footpaths_OSM',0.05,(220.5,224.0,195.0,206.5))):
    o=bpy.data.objects[on]
    assert all(abs(o.matrix_world[i][j]-(1 if i==j else 0))<1e-6 for i in range(4) for j in range(4)), on+' not identity'
    g=bpy.data.node_groups.new('QO_NE_lift_drape_'+on,'GeometryNodeTree')
    g.interface.new_socket('Geometry',in_out='INPUT',socket_type='NodeSocketGeometry'); g.interface.new_socket('Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry')
    N=g.nodes; L=g.links; gi=N.new('NodeGroupInput'); go=N.new('NodeGroupOutput')
    j=N.new('GeometryNodeJoinGeometry')
    for gobj in grounds:
      oi=N.new('GeometryNodeObjectInfo'); oi.transform_space='RELATIVE'; oi.inputs['Object'].default_value=gobj; L.new(oi.outputs['Geometry'],j.inputs[0])
    pos=N.new('GeometryNodeInputPosition'); sep=N.new('ShaderNodeSeparateXYZ'); L.new(pos.outputs[0],sep.inputs[0])
    up=N.new('ShaderNodeVectorMath'); up.operation='ADD'; L.new(pos.outputs[0],up.inputs[0]); up.inputs[1].default_value=(0,0,30)
    rc=N.new('GeometryNodeRaycast'); L.new(j.outputs[0],rc.inputs['Target Geometry']); L.new(up.outputs[0],rc.inputs['Source Position'])
    rc.inputs['Ray Direction'].default_value=(0,0,-1); rc.inputs['Ray Length'].default_value=60
    hs=N.new('ShaderNodeSeparateXYZ'); L.new(rc.outputs['Hit Position'],hs.inputs[0])
    hz=N.new('ShaderNodeMath'); hz.operation='ADD'; L.new(hs.outputs['Z'],hz.inputs[0]); hz.inputs[1].default_value=off
    dz=N.new('ShaderNodeMath'); dz.operation='SUBTRACT'; L.new(sep.outputs['Z'],dz.inputs[0]); L.new(hz.outputs[0],dz.inputs[1])
    c1=N.new('FunctionNodeCompare'); c1.data_type='FLOAT'; c1.operation='GREATER_THAN'; L.new(dz.outputs[0],c1.inputs[0]); c1.inputs[1].default_value=0.02
    c2=N.new('FunctionNodeCompare'); c2.data_type='FLOAT'; c2.operation='LESS_THAN'; L.new(dz.outputs[0],c2.inputs[0]); c2.inputs[1].default_value=1.0
    conds=[rc.outputs['Is Hit'],c1.outputs[0],c2.outputs[0]]
    for ax,lo,hi in (('X',box[0],box[1]),('Y',box[2],box[3])):
      a=N.new('FunctionNodeCompare'); a.data_type='FLOAT'; a.operation='GREATER_THAN'; L.new(sep.outputs[ax],a.inputs[0]); a.inputs[1].default_value=lo
      b=N.new('FunctionNodeCompare'); b.data_type='FLOAT'; b.operation='LESS_THAN'; L.new(sep.outputs[ax],b.inputs[0]); b.inputs[1].default_value=hi
      conds+=[a.outputs[0],b.outputs[0]]
    acc=conds[0]
    for c in conds[1:]:
      a=N.new('FunctionNodeBooleanMath'); a.operation='AND'; L.new(acc,a.inputs[0]); L.new(c,a.inputs[1]); acc=a.outputs[0]
    cmb=N.new('ShaderNodeCombineXYZ'); L.new(sep.outputs['X'],cmb.inputs[0]); L.new(sep.outputs['Y'],cmb.inputs[1]); L.new(hz.outputs[0],cmb.inputs[2])
    sp=N.new('GeometryNodeSetPosition'); L.new(gi.outputs[0],sp.inputs['Geometry']); L.new(acc,sp.inputs['Selection']); L.new(cmb.outputs[0],sp.inputs['Position'])
    L.new(sp.outputs[0],go.inputs[0])
    m=o.modifiers.new('QO_NE_lift_drape','NODES'); m.node_group=g
    o['UNVERIFIED_qo']='qo: NE lift drape box %s off %g (single centre ray onto terrain/qj fill/3DEP skirt)'%(box,off)
  print('QO lift GN added')

def fill_sink():
  # the QJ fill cells poked through the road edge at ~(221.5,215.3) as a pale box: sink them 0.35 m in a small box
  o=bpy.data.objects['QJ_NE_seam_fill_UNVERIFIED']
  g=bpy.data.node_groups.new('QO_fill_sink_under_road','GeometryNodeTree')
  g.interface.new_socket('Geometry',in_out='INPUT',socket_type='NodeSocketGeometry'); g.interface.new_socket('Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry')
  N=g.nodes; L=g.links; gi=N.new('NodeGroupInput'); go=N.new('NodeGroupOutput')
  pos=N.new('GeometryNodeInputPosition'); sep=N.new('ShaderNodeSeparateXYZ'); L.new(pos.outputs[0],sep.inputs[0])
  M=o.matrix_world.inverted()
  lo=M@Vector((219.0,213.0,0)); hi=M@Vector((224.0,217.2,0))
  conds=[]
  for ax,a0,a1 in (('X',min(lo.x,hi.x),max(lo.x,hi.x)),('Y',min(lo.y,hi.y),max(lo.y,hi.y))):
    a=N.new('FunctionNodeCompare'); a.data_type='FLOAT'; a.operation='GREATER_THAN'; L.new(sep.outputs[ax],a.inputs[0]); a.inputs[1].default_value=a0
    b=N.new('FunctionNodeCompare'); b.data_type='FLOAT'; b.operation='LESS_THAN'; L.new(sep.outputs[ax],b.inputs[0]); b.inputs[1].default_value=a1
    conds+=[a.outputs[0],b.outputs[0]]
  acc=conds[0]
  for c in conds[1:]:
    a=N.new('FunctionNodeBooleanMath'); a.operation='AND'; L.new(acc,a.inputs[0]); L.new(c,a.inputs[1]); acc=a.outputs[0]
  sp=N.new('GeometryNodeSetPosition'); sp.inputs['Offset'].default_value=(0,0,-0.35)
  L.new(gi.outputs[0],sp.inputs['Geometry']); L.new(acc,sp.inputs['Selection']); L.new(sp.outputs[0],go.inputs[0])
  m=o.modifiers.new('QO_fill_sink_under_road','NODES'); m.node_group=g
  o['UNVERIFIED_qo']='qo: fill cells in x 219-224 y 213-217.2 sunk 0.35 m under the road edge (GN)'
  print('QO fill sink GN added')

revert()
if not REV:
  im=bpy.data.images.get('ortho2020_north.jpg.001')
  if im: im['qo_prev_path']=im.filepath; im.filepath='//north/data/ortho2020_north.jpg'; print('QO repath',im.filepath, os.path.exists(bpy.path.abspath(im.filepath)))
  tone_mask(); podium(); lift()  # fill_sink() tested: opened a notch under the road edge -> not applied
  if os.environ.get('NOGRASS')!='1': grass()
if '--save' in sys.argv:
  bpy.ops.wm.save_mainfile(); print('SAVED')
