import bpy
from mathutils import Vector
for o in bpy.data.objects:
    if o.type!='MESH': continue
    if any(s.material and s.material.name.startswith('BD_fill_massing') for s in o.material_slots):
        bb=[o.matrix_world@Vector(c) for c in o.bound_box]; xs=[v.x for v in bb]; ys=[v.y for v in bb]
        print('BD',o.name,o.hide_render,round(min(xs)),round(max(xs)),round(min(ys)),round(max(ys)),round(min(v.z for v in bb),1),round(max(v.z for v in bb),1),dict(o.items()) if len(o.keys())<6 else list(o.keys()))
m=bpy.data.materials['BD_fill_massing']; print('NODES',[n.bl_idname+':'+n.name for n in m.node_tree.nodes])
