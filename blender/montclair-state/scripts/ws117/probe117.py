import bpy
from mathutils import Vector
X0,X1,Y0,Y1=-219,-205,-204,-178
for o in bpy.data.objects:
    if o.type!='MESH': continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    if max(v.x for v in bb)<X0 or min(v.x for v in bb)>X1 or max(v.y for v in bb)<Y0 or min(v.y for v in bb)>Y1: continue
    if o.name.startswith(('T_','Tree')): continue
    print('P117',o.name[:80],'hide',o.hide_render,'bb x %.1f..%.1f y %.1f..%.1f z %.1f..%.1f'%(min(v.x for v in bb),max(v.x for v in bb),min(v.y for v in bb),max(v.y for v in bb),min(v.z for v in bb),max(v.z for v in bb)),[m.type for m in o.modifiers][:3])
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
for y in (-202,-200,-198.5,-197,-195,-192,-188,-184,-180):
    out=[]
    for x in (-218,-217,-216,-215,-214,-213,-212.5,-212,-211.5,-211,-210,-209):
        h=sc.ray_cast(dg,Vector((x,y,160)),Vector((0,0,-1)))
        out.append('%s:%.2f'%(h[4].name[:14],h[1].z) if h[0] else '-')
    print('R117 y',y,' | '.join(out))
# horizontal rays at z 125.5 eastward to find the wall
for y in (-201,-199,-197,-195,-190,-185,-180):
    h=sc.ray_cast(dg,Vector((-225,y,125.6)),Vector((1,0,0)),30)
    print('W117 y',y, (h[4].name[:40],round(h[1].x,2)) if h[0] else None)
