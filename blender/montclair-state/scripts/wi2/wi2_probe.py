import bpy
O=bpy.data.objects
BX=(130,160,280,310)
for o in O:
    if o.type!='MESH': continue
    if 'grass' not in o.name.lower() and not o.name.startswith(('WV','QS_service','QS_footway_546643369','QT_soil_edge_546643369')): continue
    bb=[o.matrix_world@__import__('mathutils').Vector(c) for c in o.bound_box]
    xs=[b.x for b in bb]; ys=[b.y for b in bb]
    if not (min(xs)<BX[1] and max(xs)>BX[0] and min(ys)<BX[3] and max(ys)>BX[2]): continue
    m=o.matrix_world
    n=sum(1 for v in o.data.vertices if BX[0]<(m@v.co).x<BX[1] and BX[2]<(m@v.co).y<BX[3])
    mods=[(md.type, md.name, getattr(md,'node_group',None) and md.node_group.name) for md in o.modifiers]
    print('OBJ',o.name,len(o.data.vertices),'inbox',n,mods,[s.material.name if s.material else None for s in o.material_slots][:3], 'parsys',len(o.particle_systems))
