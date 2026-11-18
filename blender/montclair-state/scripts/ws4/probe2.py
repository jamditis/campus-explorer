import bpy
from mathutils import Vector
def bb(o):
  cs=[o.matrix_world@Vector(c) for c in o.bound_box]
  return [round(min(c[i] for c in cs),1) for i in range(3)]+[round(max(c[i] for c in cs),1) for i in range(3)]
for o in bpy.data.objects:
  n=o.name
  if o.type=='MESH' and (n.startswith('Cole') or 'Cole Hall' in n or n.startswith('Morehead') or 'Morehead Hall' in n or n.startswith('Building')) and len(o.data.vertices)>50:
    b=bb(o)
    if b[0]>-200 and b[3]<50 and b[1]>-150 and b[4]<50: print('B',n,b)
F=bpy.data.objects['Footpaths_OSM']; mw=F.matrix_world
cells={}
for p in F.data.polygons:
  c=mw@p.center
  if -90<c.x<-40 and -75<c.y<-15:
    k=(int(c.x//5)*5,int(c.y//5)*5); cells[k]=cells.get(k,0)+1
print('WALKCELLS',sorted(cells.items()))
