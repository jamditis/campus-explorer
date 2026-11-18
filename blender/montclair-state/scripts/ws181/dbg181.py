import collections
cam=Vector((-354.0,-228.8,gz2(-354.0,-228.8)+1.6)); tgt=Vector((-318.0,-226.0,gz2(-318.0,-226.0)+0.3))
d0=(tgt-cam).normalized(); right=d0.cross(Vector((0,0,1))).normalized(); up=right.cross(d0)
dg=bpy.context.evaluated_depsgraph_get(); out=[]
for u in (650,720,780,850):
  for v in (400,440,480):
    a=(u/896-0.5)*36/28; b=(0.5-v/504)*36*(504/896)/28
    d=(d0+right*a+up*b).normalized()
    ok,loc,n,i,ob,m=sc.ray_cast(dg,cam,d)
    out.append((u,v,round(loc.x,1),round(loc.y,1),round(loc.z,3),ob.name[:28] if ok else None, tuple(round(c,2) for c in n)))
for o in out: print('DBG181',o,flush=True)
