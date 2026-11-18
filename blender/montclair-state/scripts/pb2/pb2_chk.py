import bpy, mathutils, statistics as st, math
from mathutils import Vector
dg=bpy.context.evaluated_depsgraph_get()
ter=bpy.data.objects['Terrain_LiDAR_DTM_1m'].evaluated_get(dg); fp=bpy.data.objects['Footpaths_OSM'].evaluated_get(dg)
ob=bpy.data.objects['PB2_walk_lawn_fillet_UNVERIFIED']; me=ob.data
def z(o,x,y):
  r=o.ray_cast(Vector((x,y,500)),Vector((0,0,-1))); return r[1].z if r[0] else None
dt=[];dw=[]
for p in me.polygons:
  vs=[me.vertices[i].co for i in p.vertices]
  for i,v in enumerate(vs):
    pass
inn=set();out=set()
for p in me.polygons: a,b,c,d=p.vertices; inn|={a,b}; out|={c,d}
for i in out:
  v=me.vertices[i].co; t=z(ter,v.x,v.y); 
  if t is not None: dt.append(v.z-t)
for i in list(inn)[::5]:
  v=me.vertices[i].co; w=z(fp,v.x,v.y+0.0)
  if w is not None: dw.append(v.z-w)
print("CHK outer-terrain mean %.3f min %.3f max %.3f n %d"%(st.mean(dt),min(dt),max(dt),len(dt)))
print("CHK inner-walk mean %.4f min %.3f max %.3f n %d"%(st.mean(dw),min(dw),max(dw),len(dw)))
sl=[math.degrees(math.acos(min(1,abs(p.normal.z)))) for p in me.polygons]; print("CHK slope deg min %.1f mean %.1f"%(min(sl),st.mean(sl)), "flat(<0.5deg)",sum(s<0.5 for s in sl))
kd=mathutils.kdtree.KDTree(len(me.vertices))
for i,v in enumerate(me.vertices): kd.insert(v.co,i)
kd.balance(); hit=[]
for o in bpy.data.objects:
  n=o.name.lower()
  if o.type in('MESH','EMPTY') and any(k in n for k in('lamp','bench','bin','bollard','bike','sign','trash','light_pole','post')):
    p=o.matrix_world.translation
    if -150<p.x<150 and 130<p.y<260:
      c,i,d=kd.find(p)
      if d<0.8: hit.append((o.name,round(d,2)))
print("CHK furniture within 0.8 m of fillet:",len(hit),hit[:10])
