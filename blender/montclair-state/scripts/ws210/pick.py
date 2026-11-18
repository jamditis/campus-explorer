import bpy, json, os, math
from mathutils import Vector
S='/workspace/nj-scenes/montclair-state/scripts/'
BB=json.load(open(S+'ws205/bbox205.json')); cx0,cx1,cy0,cy1=-240,-170,-130,-70
want=[n for n,(t,hr,x0,x1,y0,y1,z0,z1,cols) in BB.items() if t=='MESH' and not hr and not n.startswith(('Context_skirt','BD_farfield')) and not (x1<cx0 or x0>cx1 or y1<cy0 or y0>cy1)]
with bpy.data.libraries.load('/workspace/nj-scenes/montclair-state/montclair_state.blend') as (a,b): b.objects=[n for n in want if n in set(a.objects)]
sc=bpy.context.scene
for o in b.objects:
    sc.collection.objects.link(o)
    for m in o.modifiers: m.show_viewport=False
dg=bpy.context.evaluated_depsgraph_get()
c=Vector((-214,-104,127.9)); t=Vector((-195,-90,128)); f=(t-c).normalized()
r=f.cross(Vector((0,0,1))).normalized(); u=r.cross(f)
w=36/2/24; h=w*396/704
for px,py in [(650,60),(600,120),(690,150),(520,30),(120,180),(30,150),(600,300),(650,350)]:
    nx=(px/704*2-1)*w; ny=(1-py/396*2)*h
    d=(f+r*nx+u*ny).normalized()
    hit,loc,nor,idx,ob,mx=sc.ray_cast(dg,c,d)
    print('PK',px,py,ob.name if ob else None, tuple(round(v,1) for v in loc) if hit else None, ob.material_slots[ob.data.polygons[idx].material_index].name if hit and ob.material_slots else '',flush=True)
