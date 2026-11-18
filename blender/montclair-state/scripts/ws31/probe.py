import bpy
from mathutils import Vector
X0,X1,Y0,Y1=-15,10,-55,-18
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
for o in sc.objects:
    if o.type!='MESH' or o.hide_render: continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    if max(p.x for p in bb)<X0 or min(p.x for p in bb)>X1 or max(p.y for p in bb)<Y0 or min(p.y for p in bb)>Y1: continue
    mw=o.matrix_world; zs=[(mw@v.co) for v in o.data.vertices]
    zs=[p for p in zs if X0<p.x<X1 and Y0<p.y<Y1]
    if not zs: continue
    print('OBJ %-55s n=%5d z %.2f..%.2f users=%d'%(o.name[:55],len(zs),min(p.z for p in zs),max(p.z for p in zs),o.data.users))
# grid of hits: top-hit object and terrain z
ter=bpy.data.objects['Terrain_LiDAR_DTM_1m']
for y in range(-54,-18,3):
    row=[]
    for x in range(-14,10,3):
        h=sc.ray_cast(dg,Vector((x,y,170)),Vector((0,0,-1)))
        row.append('%s:%.2f'%(h[4].name[:8] if h[0] else '-',h[1].z if h[0] else 0))
    print(y,' '.join(row))
