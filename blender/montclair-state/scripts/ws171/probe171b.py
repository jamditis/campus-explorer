import bpy, math
from mathutils import Vector
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws166/hdr166.py').read())
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
c=Vector((-312.5,-243.5,dz(-312.5,-243.5)+1.6)); t=Vector((-301.5,-234.5,dz(-301.5,-234.5)+0.3))
f=(t-c).normalized(); r=f.cross(Vector((0,0,1))).normalized(); u=r.cross(f)
tw=math.tan(math.atan(18/28)); th=tw*9/16
for (px,py) in [(530,172),(545,176),(560,178),(540,182),(470,176),(600,170),(540,165)]:
    nx=(px/768-0.5)*2; ny=(0.5-py/432)*2
    d=(f+r*nx*tw+u*ny*th).normalized()
    hit,loc,nor,idx,ob,_=sc.ray_cast(dg,c,d)
    if not hit: print('PROBE171b',px,py,None); continue
    ev=ob.evaluated_get(dg); me=ev.data; p=me.polygons[idx] if idx<len(me.polygons) else None
    mat=ev.material_slots[p.material_index].material.name if p and ev.material_slots and ev.material_slots[p.material_index].material else None
    print('PROBE171b',px,py,ob.name,tuple(round(a,2) for a in loc),'n',tuple(round(a,2) for a in nor),'n.d',round(nor.dot(d),2),'mat',mat,'dtm',round(dz(loc.x,loc.y),2),flush=True)
    # what is just below along the wall: cast horizontally toward the wall at ground+0.2
    h2=sc.ray_cast(dg,Vector((loc.x-3*d.x,loc.y-3*d.y,dz(loc.x,loc.y)+0.2)),Vector((d.x,d.y,0)).normalized())
    print('PROBE171b  low',h2[4].name if h2[0] else None,tuple(round(a,2) for a in h2[1]) if h2[0] else None,flush=True)
