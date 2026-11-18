import bpy
from mathutils import Vector
ws=set(o.name for o in bpy.data.collections['WS66_RedHawkDeck_from_north'].all_objects)
for o in bpy.data.objects:
    if o.name in ws or o.type not in('MESH','EMPTY','CURVE'): continue
    bb=[o.matrix_world@Vector(v) for v in o.bound_box]
    xs=[p.x for p in bb];ys=[p.y for p in bb];zs=[p.z for p in bb]
    if max(xs)<-345 or min(xs)>-225 or max(ys)<-105 or min(ys)>40: continue
    big=max(xs)-min(xs)>600
    print('N68 %-50s %s f=%7d x%7.1f..%7.1f y%7.1f..%7.1f z%6.1f..%6.1f hr=%d mods=%s cols=%s'%(o.name[:50],o.type,len(o.data.polygons) if o.type=='MESH' else 0,min(xs),max(xs),min(ys),max(ys),min(zs),max(zs),o.hide_render,','.join(m.type for m in o.modifiers)[:30],','.join(c.name[:20] for c in o.users_collection)))
