# pc: grass clump scatter on the pb2 walk/lawn fillet + a fading 1.2 m margin onto the lawn beyond it (north strip CELS/Calcia).
# Removable: REVERT=1 deletes collection PC_fillet_grass_20261101pc + its objects/meshes. Static points built from the EVALUATED
# PB2 fillet + terrain; instanced with the existing cx_grass_instancer (Main_grass_cx_clumps). UNVERIFIED (no photo of these lawn edges).
import bpy, bmesh, os, sys, random, math
from mathutils import Vector
COL='PC_fillet_grass_20261101pc'; OBN='PC_fillet_grass_points_UNVERIFIED'
D=float(os.environ.get('D','22'))      # points / m2 on the fillet
MW=float(os.environ.get('MW','1.2'))   # margin width beyond the fillet outer edge (m), density fades to 0
DM=float(os.environ.get('DM','0.8'))   # margin density factor at the fillet edge
SEED=int(os.environ.get('SEED','1101'))
def revert():
  c=bpy.data.collections.get(COL)
  if c:
    for o in list(c.objects): bpy.data.objects.remove(o)
    bpy.data.collections.remove(c)
  for me in [m for m in bpy.data.meshes if m.name.startswith(OBN) and m.users==0]: bpy.data.meshes.remove(me)
  print("REVERTED")
revert()
if os.environ.get('REVERT')!='1':
  rnd=random.Random(SEED); dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
  ter=bpy.data.objects['Terrain_LiDAR_DTM_1m'].evaluated_get(dg)
  blk=[bpy.data.objects[n].evaluated_get(dg) for n in ('Footpaths_OSM','Roads_OSM')]
  fil=bpy.data.objects['PB2_walk_lawn_fillet_UNVERIFIED'].data
  V=[v.co.copy() for v in fil.vertices]
  pts=[]; nf=nm=nb=0
  def blocked(p):
    for o in blk:
      r=o.ray_cast(Vector((p.x,p.y,p.z+3)),Vector((0,0,-1)),distance=3.2)
      if r[0] and r[1].z>p.z-0.05: return True
    return False
  for poly in fil.polygons:
    # pb2 creates each (inner, outer) pair consecutively -> inner verts have even indices, outer = inner+1
    inn=sorted(i for i in poly.vertices if i%2==0)
    if len(inn)!=2 or any(i+1 not in poly.vertices for i in inn): continue
    ia,ib=V[inn[0]],V[inn[1]]; oa,ob=V[inn[0]+1],V[inn[1]+1]
    L=((ia-ib).length+(oa-ob).length)/2; Wd=((ia-oa).length+(ib-ob).length)/2
    if L<1e-3 or Wd<1e-3: continue
    # fillet part
    n=int(D*poly.area+rnd.random())
    for _ in range(n):
      s=rnd.random(); t=rnd.random()*0.92+0.08   # keep the first 8% next to the slab clear
      pi=ia.lerp(ib,s); po=oa.lerp(ob,s); p=pi.lerp(po,t); p.z-=0.005
      pts.append(p); nf+=1
    # margin beyond the outer edge (fading density)
    d2=(oa.lerp(ob,0.5)-ia.lerp(ib,0.5)); d2.z=0
    if d2.length<1e-3: continue
    d2.normalize(); n=int(D*DM*0.5*L*MW+rnd.random())
    for _ in range(n):
      s=rnd.random(); u=1-math.sqrt(rnd.random())   # triangular falloff: dense at the edge
      q=oa.lerp(ob,s)+d2*(u*MW)
      r=ter.ray_cast(Vector((q.x,q.y,q.z+5)),Vector((0,0,-1)))
      if not r[0]: continue
      p=Vector((q.x,q.y,r[1].z-0.005))
      if blocked(p): nb+=1; continue
      pts.append(p); nm+=1
  # extra clumps round the dark walk-corner notch at the bottom-right of the OQ Calcia view (gap between a tilted walk corner and the fillet)
  NX,NY,NR=[float(v) for v in os.environ.get('NOTCH','-121.7,205.05,0.7').split(',')]; nn=0
  for _ in range(int(D*1.5*math.pi*NR*NR)):
    a=rnd.random()*2*math.pi; r0=NR*math.sqrt(rnd.random()); q=Vector((NX+r0*math.cos(a),NY+r0*math.sin(a),0))
    hz=None
    for o in (ter,bpy.data.objects['PB2_walk_lawn_fillet_UNVERIFIED']):
      r=o.ray_cast(Vector((q.x,q.y,145)),Vector((0,0,-1)))
      if r[0] and (hz is None or r[1].z>hz): hz=r[1].z
    if hz is None: continue
    p=Vector((q.x,q.y,hz-0.005))
    if blocked(p): continue
    pts.append(p); nn+=1
  print("PCNOTCH",nn)
  me=bpy.data.meshes.new(OBN); me.from_pydata([tuple(p) for p in pts],[],[])
  ob=bpy.data.objects.new(OBN,me); c=bpy.data.collections.new(COL); sc.collection.children.link(c); c.objects.link(ob)
  src=bpy.data.objects['cx_grass_points'].modifiers['cx_grass']
  m=ob.modifiers.new('cx_grass','NODES'); m.node_group=src.node_group
  ob['pc_fillet_grass']='D=%.1f MW=%.2f DM=%.2f SEED=%d NOTCH=%s'%(D,MW,DM,SEED,os.environ.get('NOTCH','-121.7,205.05,0.7'))
  print("PCGRASS pts",len(pts),"fillet",nf,"margin",nm,"blocked",nb)
if '--save' in sys.argv: bpy.ops.wm.save_mainfile(); print("SAVED")
