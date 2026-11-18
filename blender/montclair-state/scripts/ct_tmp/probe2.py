import bpy
from mathutils import Vector
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
code={}
def c(o):
  n=o.name
  for k,v in [('Terrain','g'),('Kasser Theater roof','K'),('Kasser Theater walls','W'),('plaza_deck','d'),('plaza_edge','e'),('pavilion','p'),('long arched','L')]:
    if k in n: return v
  return '?'
others=set()
for y in [ -48+(-1.0)*i for i in range(0,26)]:
  row=[]
  for x in [-200+1.0*j for j in range(0,32)]:
    h,l,nn,i,o,m=sc.ray_cast(dg,Vector((x,y,200)),Vector((0,0,-1)))
    ch=c(o) if o else ' '
    if ch=='?': others.add(o.name[:50])
    row.append('%s%3d'%(ch,int(round((l.z-128)*10))) if h else '  - ')
  print('Y%6.1f '%y+' '.join(row))
print(others)
