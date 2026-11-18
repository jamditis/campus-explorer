# pb2: lawn fillet overlay where Footpaths_OSM slab edges stand above the lawn (north strip CELS/Calcia).
# Removable: REVERT=1 deletes collection PB2_walk_lawn_fillet_20261101pb2 + its objects. Static overlay built from EVALUATED walks/terrain.
import bpy, bmesh, mathutils, os, sys, statistics as st
from mathutils import Vector
COL='PB2_walk_lawn_fillet_20261101pb2'; OBN='PB2_walk_lawn_fillet_UNVERIFIED'
W=float(os.environ.get('W','0.35')); EMB=float(os.environ.get('EMB','0.02')); TOP=float(os.environ.get('TOP','0.004'))
BOX=[float(v) for v in os.environ.get('BOX','-150,150,130,260').split(',')]
LMIN=float(os.environ.get('LMIN','0.012')); LMAX=float(os.environ.get('LMAX','0.30'))
def revert():
  c=bpy.data.collections.get(COL)
  if c:
    for o in list(c.objects): m=o.data; bpy.data.objects.remove(o); 
    bpy.data.collections.remove(c)
  for me in [m for m in bpy.data.meshes if m.name.startswith(OBN) and m.users==0]: bpy.data.meshes.remove(me)
  cc=bpy.data.collections.get('PB2_cams_20261101pb2')
  if cc:
    for o in list(cc.objects): d=o.data; bpy.data.objects.remove(o); bpy.data.cameras.remove(d)
    bpy.data.collections.remove(cc)
  print("REVERTED")
revert()
if os.environ.get('REVERT')!='1':
  dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
  ter=bpy.data.objects['Terrain_LiDAR_DTM_1m'].evaluated_get(dg)
  fp=bpy.data.objects['Footpaths_OSM'].evaluated_get(dg); me=fp.to_mesh(); mw=fp.matrix_world
  bm=bmesh.new(); bm.from_mesh(me); bm.transform(mw); bm.verts.ensure_lookup_table(); bm.faces.ensure_lookup_table()
  blk=[bpy.data.objects[n].evaluated_get(dg) for n in ('Footpaths_OSM','Roads_OSM')]
  FK=float(os.environ.get('FK','0.6')); KW=('lamp','bench','bin','bollard','bike','sign','trash','light_pole','post')
  furn=[o.matrix_world.translation.copy() for o in bpy.data.objects if o.type in('MESH','EMPTY') and any(k in o.name.lower() for k in KW)]
  def nearf(p): return any((f.x-p.x)**2+(f.y-p.y)**2<(FK+W)**2 for f in furn)
  def inb(p): return BOX[0]<=p.x<=BOX[1] and BOX[2]<=p.y<=BOX[3]
  def tz(x,y):
    r=ter.ray_cast(Vector((x,y,500)),Vector((0,0,-1)))
    return (r[1].z, r[3]) if r[0] else (None,None)
  # outward normals per boundary edge
  en={}
  for e in bm.edges:
    if not e.is_boundary or len(e.link_faces)!=1: continue
    a,b=e.verts; m=(a.co+b.co)/2
    if not inb(m): continue
    if nearf(a.co) or nearf(b.co): continue
    d=(b.co-a.co); d.z=0
    if d.length<1e-4: continue
    n=Vector((d.y,-d.x,0)).normalized(); fc=e.link_faces[0].calc_center_median()
    if n.dot(fc-m)>0: n=-n
    # lip check at edge midpoint just outside
    z,_=tz(m.x+n.x*0.05,m.y+n.y*0.05)
    if z is None: continue
    lip=m.z-z
    if lip<LMIN or lip>LMAX: continue
    # outer point must land on terrain (not road/walk/building)
    o=m+n*W*0.9; blocked=False
    for ob2 in blk:
      r=ob2.ray_cast(Vector((o.x,o.y,m.z+3)),Vector((0,0,-1)),distance=3.5)
      if r[0]: blocked=True; break
    if blocked: continue
    en[e.index]=(e,n,lip)
  vn={}
  for e,n,_ in en.values():
    for v in e.verts: vn[v.index]=vn.get(v.index,Vector())+n
  out=bmesh.new(); inner={}; outer={}; mats=[]; matmap={}
  tm=bpy.data.objects['Terrain_LiDAR_DTM_1m'].data.materials
  def vpair(v):
    if v.index in inner: return inner[v.index],outer[v.index]
    n=vn[v.index]; n.z=0; n=n.normalized()
    iv=out.verts.new(Vector((v.co.x,v.co.y,v.co.z-TOP)))
    p=v.co+n*W; z,fi=tz(p.x,p.y)
    if z is None: z=v.co.z-0.1
    ov=out.verts.new(Vector((p.x,p.y,z-EMB)))
    inner[v.index]=iv; outer[v.index]=ov; return iv,ov
  lips=[]
  for e,n,lip in en.values():
    a,b=e.verts; ia,oa=vpair(a); ib,ob=vpair(b)
    # orient so normal points up
    try: f=out.faces.new((ia,ib,ob,oa))
    except ValueError: continue
    if f.normal.z<0: f.normal_flip()
    m=(a.co+b.co)/2+n*W*0.5; _,fi=tz(m.x,m.y)
    mi=ter.data.polygons[fi].material_index if fi is not None and fi<len(ter.data.polygons) else 0
    f.material_index=mi; lips.append(lip)
  uvl=out.loops.layers.uv.new('ortho')
  for f in out.faces:
    for l in f.loops: l[uvl].uv=(0.002*l.vert.co.x+0.5, 0.002*l.vert.co.y+0.5)
  m2=bpy.data.meshes.new(OBN); out.to_mesh(m2)
  for mat in tm: m2.materials.append(mat)
  for p in m2.polygons: p.use_smooth=True
  ob=bpy.data.objects.new(OBN,m2); c=bpy.data.collections.new(COL); sc.collection.children.link(c); c.objects.link(ob)
  ob['pb2_walk_lawn_fillet']='W=%.2f EMB=%.3f TOP=%.3f BOX=%s'%(W,EMB,TOP,BOX)
  print("FILLET faces",len(m2.polygons),"verts",len(m2.vertices),"lip mean %.3f min %.3f max %.3f"%(st.mean(lips),min(lips),max(lips)) if lips else "none")
  fp.to_mesh_clear()
  import math
  src=bpy.data.objects['OQ_CAM_eye_calcia_skirt_windows']; cd=src.data.copy(); cd.name='PB2_CAM_closeup_calcia_walk_lawn_fillet'; cd.lens=float(os.environ.get('CLENS','30'))
  cam=bpy.data.objects.new('PB2_CAM_closeup_calcia_walk_lawn_fillet',cd); e=src.matrix_world.to_euler()
  fw=Vector((math.cos(e.z+math.pi/2),math.sin(e.z+math.pi/2),0)); lf=Vector((-fw.y,fw.x,0))
  cam.location=src.matrix_world.translation+fw*float(os.environ.get('CF','3'))+lf*float(os.environ.get('CL','1.5'))+Vector((0,0,float(os.environ.get('CZ','-0.5'))))
  cam.rotation_euler=(e.x-math.radians(float(os.environ.get('CP','18'))),0,e.z+math.radians(float(os.environ.get('CY','12'))))
  cc=bpy.data.collections.new('PB2_cams_20261101pb2'); sc.collection.children.link(cc); cc.objects.link(cam)
if '--save' in sys.argv: bpy.ops.wm.save_mainfile(); print("SAVED")
