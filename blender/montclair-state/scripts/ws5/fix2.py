import bpy, bmesh, json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
D='/workspace/nj-scenes/montclair-state/scripts/ws5/'
P=json.load(open(D+'pieces.json')); ring=[tuple(c) for c in P['union']['coordinates'][0]]
def pin(x,y,r=ring):
  ins=False; n=len(r); j=n-1
  for i in range(n):
    xi,yi=r[i]; xj,yj=r[j]
    if (yi>y)!=(yj>y) and x<(xj-xi)*(y-yi)/(yj-yi+1e-12)+xi: ins=not ins
    j=i
  return ins
PL=bpy.data.objects['WS5_Cole_plaza_circle_quatrefoil_20261109']
pv=[PL.matrix_world@v.co for v in PL.data.vertices]; PB=BVHTree.FromPolygons(pv,[list(f.vertices) for f in PL.data.polygons])
def near_plaza(x,y):
  for dx,dy in ((0,0),(0.35,0),(-0.35,0),(0,0.35),(0,-0.35)):
    h=PB.ray_cast(Vector((x+dx,y+dy,300)),Vector((0,0,-1)))
    if h[0]: return h[0].z
  return None
# 1. planting-bed verts under/at the plaza edge dip below the plaza surface
B=bpy.data.objects['COLE_planting_beds_smooth_bu']; mw=B.matrix_world; mi=mw.inverted(); n=0
for v in B.data.vertices:
  w=mw@v.co; z=near_plaza(w.x,w.y)
  if z is not None and w.z>z-0.08:
    w.z=z-0.08; v.co=mi@w; n+=1
B.data.update(); print('bed verts lowered',n)
# 2. WS3 paving: drop small leftover islands (<6 m2) near the plaza
W=bpy.data.objects['WS3_Cole_plaza_paving_20261109']; bm=bmesh.new(); bm.from_mesh(W.data); bm.faces.ensure_lookup_table()
seen=set(); kill=[]
for f in bm.faces:
  if f.index in seen: continue
  isl=[]; st=[f]; seen.add(f.index)
  while st:
    g=st.pop(); isl.append(g)
    for e in g.edges:
      for h in e.link_faces:
        if h.index not in seen: seen.add(h.index); st.append(h)
  a=sum(x.calc_area() for x in isl); c=sum((x.calc_center_median() for x in isl),Vector())/len(isl)
  c=W.matrix_world@c
  if a<6.0 and -124<c.x<-90 and -68<c.y<-36: kill+=isl; print('island',round(a,2),[round(c.x,1),round(c.y,1)],len(isl))
bmesh.ops.delete(bm,geom=kill,context='FACES'); bm.to_mesh(W.data); bm.free(); print('killed faces',len(kill))
bpy.ops.wm.save_mainfile(); print('SAVED')
