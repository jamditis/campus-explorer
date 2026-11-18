import bpy, bmesh, math, json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
W=bpy.data.objects['WS3_Cole_plaza_paving_20261109']
wv=[W.matrix_world@v.co for v in W.data.vertices]
WB=BVHTree.FromPolygons(wv,[list(f.vertices) for f in W.data.polygons])
PL=bpy.data.objects['WS5_Cole_plaza_circle_quatrefoil_20261109']
pv=[PL.matrix_world@v.co for v in PL.data.vertices]; PB=BVHTree.FromPolygons(pv,[list(f.vertices) for f in PL.data.polygons])
def hit(B,x,y):
  h=B.ray_cast(Vector((x,y,300)),Vector((0,0,-1))); return h[0].z if h[0] else None
for sx in (-117.5,-118.5,-119.5,-121.0,-123.0):
  print('ROW',sx,''.join(('P' if hit(PB,sx,-44-i*0.25) else '#') if hit(WB,sx,-44-i*0.25) is not None else ('P' if hit(PB,sx,-44-i*0.25) else '.') for i in range(64)))
# islands near the sign closeup stray slab
bm=bmesh.new(); bm.from_mesh(W.data); seen=set()
for f in bm.faces:
  if f.index in seen: continue
  isl=[]; st=[f]; seen.add(f.index)
  while st:
    g=st.pop(); isl.append(g)
    for e in g.edges:
      for h in e.link_faces:
        if h.index not in seen: seen.add(h.index); st.append(h)
  vs=[W.matrix_world@v.co for g in isl for v in g.verts]
  lo=(min(v.x for v in vs),min(v.y for v in vs)); hi=(max(v.x for v in vs),max(v.y for v in vs))
  if hi[0]>-125 and lo[0]<-85 and hi[1]>-68 and lo[1]<-36:
    print('ISL',round(sum(g.calc_area() for g in isl),1),[round(x,1) for x in lo],[round(x,1) for x in hi])
bm.free()
