import bpy, bmesh, os
from mathutils import Vector
DRY=os.environ.get('DRY')=='1'
w=bpy.data.objects['WS3_Cole_plaza_paving_20261109']; mw=w.matrix_world
p=bpy.data.objects['WS5_Cole_plaza_circle_quatrefoil_20261109']
bbp=[p.matrix_world@Vector(c) for c in p.bound_box]
pc=sum(bbp,Vector())/8; pr=max(p.dimensions.x,p.dimensions.y)/2
print('PLAZA c',[round(v,2) for v in pc],'r',round(pr,2))
bm=bmesh.new(); bm.from_mesh(w.data); bm.transform(mw); bm.faces.ensure_lookup_table()
X0,X1,Y0,Y1=float(os.environ.get('X0',-97)),float(os.environ.get('X1',-66)),float(os.environ.get('Y0',-60)),float(os.environ.get('Y1',-45))
sel=set(f for f in bm.faces if X0<f.calc_center_median().x<X1 and Y0<f.calc_center_median().y<Y1)
xs=[v.co.x for f in sel for v in f.verts]; ys=[v.co.y for f in sel for v in f.verts]
print('SEL',len(sel),'bbox',round(min(xs),1),round(max(xs),1),round(min(ys),1),round(max(ys),1))
W=0.24; Z=0.007
verts=[];faces=[]
nb=0;L=0
for e in bm.edges:
  if not e.is_boundary: continue
  f=e.link_faces[0]
  if f not in sel: continue
  a,b=e.verts[0].co.copy(),e.verts[1].co.copy()
  m=(a+b)/2
  if (Vector((m.x,m.y))-Vector((pc.x,pc.y))).length<pr+0.6: continue
  if e.calc_length()<0.05: continue
  if m.x>-83.0: continue
  d=(b-a); d.z=0; d.normalize()
  n=Vector((-d.y,d.x,0)); fc=f.calc_center_median()
  if n.dot(fc-m)<0: n=-n
  i=len(verts)
  verts+= [a+Vector((0,0,Z)), b+Vector((0,0,Z)), b+n*W+Vector((0,0,Z)), a+n*W+Vector((0,0,Z))]
  faces.append((i,i+1,i+2,i+3)); nb+=1; L+=e.calc_length()
print('EDGES',nb,'LEN',round(L,1))
if not DRY:
  me=bpy.data.meshes.new('WS9_Cole_walk_brick_edging'); me.from_pydata(verts,[],faces); me.update()
  ob=bpy.data.objects.new('WS9_Cole_walk_brick_edging_toward_Morehead_20261109',me)
  me.materials.append(bpy.data.materials['WS3_Brick_soldier_course'])
  col=bpy.data.collections.get('WS9_Cole_walk_brick_edging_20261109') or bpy.data.collections.new('WS9_Cole_walk_brick_edging_20261109')
  if col.name not in bpy.context.scene.collection.children: bpy.context.scene.collection.children.link(col)
  col.objects.link(ob)
  # UVs along strip for running pattern
  me.uv_layers.new(name='UVMap')
  bpy.ops.wm.save_mainfile(); print('SAVED')
