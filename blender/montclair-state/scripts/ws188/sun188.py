import bpy, os, math
from mathutils import Vector
bpy.data.objects['Context_skirt_3DEP_ortho_4km'].hide_viewport=True
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
el=0.10471975803375244; r=4.27605676651001; ce=math.cos(el)
for nm,L in [('A',Vector((math.sin(r)*ce,math.cos(r)*ce,math.sin(el)))),('B',Vector((math.cos(r)*ce,math.sin(r)*ce,math.sin(el)))),('C',Vector((-math.sin(r)*ce,math.cos(r)*ce,math.sin(el)))),('D',Vector((math.cos(r-math.pi/2)*ce,math.sin(r-math.pi/2)*ce,math.sin(el))))]:
  for p in os.environ['PTS'].split():
    x,y=map(float,p.split(':'))
    h,loc,nor,fi,ob,_=sc.ray_cast(dg,Vector((x,y,160)),Vector((0,0,-1)))
    o=loc+nor*0.02; h2,l2,n2,f2,ob2,_=sc.ray_cast(dg,o,L)
    print('SUN188',nm,p,'shadowed by',ob2.name[:55] if h2 else None,tuple(round(c,1) for c in l2) if h2 else '',flush=True)
