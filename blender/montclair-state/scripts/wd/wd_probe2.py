import bpy, json
from mathutils import Vector
dg=bpy.context.evaluated_depsgraph_get()
for n in ['TK_Bohn_landing_N_steps_UNVERIFIED','TK_Bohn_landing_W_walk_UNVERIFIED','TK_Bohn_door_glass_W_walk_UNVERIFIED','TK_Bohn_door_glass_N_steps_UNVERIFIED','TK_Bohn_canopy_N_steps_UNVERIFIED']:
    o=bpy.data.objects[n]; bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    print(n,[round(min(v.x for v in bb),1),round(max(v.x for v in bb),1),round(min(v.y for v in bb),1),round(max(v.y for v in bb),1),round(min(v.z for v in bb),2),round(max(v.z for v in bb),2)], o.get('UNVERIFIED'))
big=[o for o in bpy.data.objects if o.type=='MESH' and not o.hide_render and o.name not in ()]
pts=[(208.9,406.0),(212.4,404.6),(215.5,403.4),(205,422.3),(212,419.8),(220,417.0),(224,415.5),(228,413.8),(199.5,427),(197,433)]
for x,y in pts:
    hits=[]
    for o in big:
        bb=[o.matrix_world@Vector(c) for c in o.bound_box]
        if not (min(v.x for v in bb)<=x<=max(v.x for v in bb) and min(v.y for v in bb)<=y<=max(v.y for v in bb)): continue
        if o.name.startswith('TL_tree') or 'grass_points' in o.name: continue
        e=o.evaluated_get(dg); mw=o.matrix_world; iw=mw.inverted()
        try: r=e.ray_cast(iw@Vector((x,y,400)),(iw.to_3x3()@Vector((0,0,-1))).normalized())
        except Exception: continue
        if r[0]: hits.append((round((mw@r[1]).z,2),o.name))
    hits.sort(reverse=True); print(x,y,hits[:6])
