import bpy, math
from mathutils import Vector
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws166/hdr166.py').read())
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
c=Vector((-312.5,-243.5,dz(-312.5,-243.5)+1.6)); t=Vector((-301.5,-234.5,dz(-301.5,-234.5)+0.3))
f=(t-c).normalized(); r=f.cross(Vector((0,0,1))).normalized(); u=r.cross(f)
tw=math.tan(math.atan(18/28)); th=tw*9/16
for (px,py) in [(530,172),(545,176),(560,178),(520,170),(540,182),(140,210),(60,222),(250,205),(420,182)]:
    nx=(px/768-0.5)*2; ny=(0.5-py/432)*2
    d=(f+r*nx*tw+u*ny*th).normalized()
    hit,loc,nor,idx,ob,_=sc.ray_cast(dg,c,d)
    print('PROBE171',px,py,ob.name if ob else None,tuple(round(a,2) for a in loc) if hit else None,'dtm',round(dz(loc.x,loc.y),2) if hit else None,flush=True)
