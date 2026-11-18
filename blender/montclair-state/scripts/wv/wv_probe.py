import bpy, json
from mathutils import Vector
X0,X1,Y0,Y1=120,155,245,320
out=[]
for o in bpy.data.objects:
    if o.type!='MESH': continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    xs=[b.x for b in bb]; ys=[b.y for b in bb]; zs=[b.z for b in bb]
    if max(xs)<X0-2 or min(xs)>X1+2 or max(ys)<Y0-2 or min(ys)>Y1+2: continue
    if max(xs)-min(xs)>400: 
        out.append(('BIG',o.name)); continue
    out.append((o.name,[round(min(xs),1),round(max(xs),1),round(min(ys),1),round(max(ys),1),round(min(zs),1),round(max(zs),1)],len(o.data.vertices),o.hide_render))
for r in out: print('OBJ',r)
print('NODEGROUPS',[n.name for n in bpy.data.node_groups if 'skirt' in n.name.lower()])
sk=bpy.data.objects['Context_skirt_3DEP_ortho_4km']; print('MODS',[m.name for m in sk.modifiers])
