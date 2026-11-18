import bpy, bmesh, os
from mathutils import Vector
DRY=os.environ.get('DRY')=='1'
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
src=bpy.data.objects['Footpaths_OSM']; ev=src.evaluated_get(dg)
me0=ev.to_mesh(); mw=src.matrix_world
bm=bmesh.new(); bm.from_mesh(me0); bm.transform(mw); bm.faces.ensure_lookup_table()
X0,X1,Y0,Y1=[float(os.environ.get(k,d)) for k,d in (('X0',-83.0),('X1',-45.5),('Y0',-60),('Y1',-49))]
top=set(f for f in bm.faces if f.normal.z>0.7)
sel=set(f for f in top if X0<f.calc_center_median().x<X1 and Y0<f.calc_center_median().y<Y1)
print('SEL',len(sel),'TOP',len(top))
skipnames=('Footpaths_OSM','WS3_Cole_plaza_paving','BikePad','Morehead','OZ_walk','WS9_')
W=0.24; Z=0.007; verts=[];faces=[];nb=0;L=0;sk=0
for e in bm.edges:
  lf=[f for f in e.link_faces if f in top]
  if len(lf)!=1 or lf[0] not in sel: continue
  f=lf[0]
  if e.calc_length()<0.05: continue
  a,b=e.verts[0].co.copy(),e.verts[1].co.copy(); m=(a+b)/2
  if not (X0<m.x<X1): continue
  d=(b-a); d.z=0; d.normalize(); n=Vector((-d.y,d.x,0))
  if n.dot(f.calc_center_median()-m)<0: n=-n
  # outward probe: if another paved surface continues past this edge, it's a junction -> skip
  r=sc.ray_cast(dg,m-n*0.35+Vector((0,0,3)),Vector((0,0,-1)))
  hitname=r[4].name if r[0] else ''
  # walk down through vegetation
  o=m-n*0.35+Vector((0,0,3)); junction=False
  for i in range(8):
    r=sc.ray_cast(dg,o,Vector((0,0,-1)))
    if not r[0]: break
    nm=r[4].name
    if nm.startswith(skipnames) and r[1].z>m.z-0.08: junction=True; break
    if nm.startswith('Terrain'): break
    o=r[1]+Vector((0,0,-0.002))
  if junction: sk+=1; continue
  i=len(verts)
  verts+=[a+Vector((0,0,Z)),b+Vector((0,0,Z)),b+n*W+Vector((0,0,Z)),a+n*W+Vector((0,0,Z))]
  faces.append((i,i+1,i+2,i+3)); nb+=1; L+=e.calc_length()
print('EDGES',nb,'LEN',round(L,1),'SKIPPED_JUNCTION',sk)
if not DRY:
  me=bpy.data.meshes.new('WS10_Morehead_walk_brick_edging'); me.from_pydata(verts,[],faces); me.update()
  ob=bpy.data.objects.new('WS10_Cole_to_Morehead_walk_brick_edging_20261109',me)
  me.materials.append(bpy.data.materials['WS3_Brick_soldier_course'])
  col=bpy.data.collections['WS9_Cole_walk_brick_edging_20261109']; col.objects.link(ob)
  me.uv_layers.new(name='UVMap')
  bpy.ops.wm.save_mainfile(); print('SAVED')
