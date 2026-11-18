import bpy
from mathutils import Vector
dg=bpy.context.evaluated_depsgraph_get()
pts={'099':(223.5,419.5),'104':(223.5,423.5),'100':(231.5,420.5),'101':(237.5,420.5),'095':(227.5,415.5)}
for k,(x,y) in pts.items():
    hits=[]
    for o in bpy.data.objects:
        if o.type!='MESH' or o.name.startswith('TL_tree') or o.hide_render: continue
        bb=[o.matrix_world@Vector(c) for c in o.bound_box]
        if not (min(p.x for p in bb)<=x<=max(p.x for p in bb) and min(p.y for p in bb)<=y<=max(p.y for p in bb)): continue
        e=o.evaluated_get(dg); inv=o.matrix_world.inverted()
        lo=inv@Vector((x,y,400)); ld=(inv@Vector((x,y,0))-lo).normalized()
        try: r=e.ray_cast(lo,ld)
        except Exception as ex: continue
        if r[0]: hits.append((round((o.matrix_world@r[1]).z,2),o.name))
    hits.sort(reverse=True); print('CV',k,hits[:6])
