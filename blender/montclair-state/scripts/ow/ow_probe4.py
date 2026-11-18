import bpy
from mathutils import Vector
C=Vector((127.25,196.1))
for o in bpy.data.objects:
    if o.type!='MESH' or not (o.name.startswith('OR_base') or o.name.startswith('OV_gapfill_base') or o.name.startswith('OT_') ): continue
    wm=o.matrix_world; me=o.data
    pts=[(wm@v.co) for v in me.vertices if ((wm@v.co).xy-C).length<2.2]
    if pts: print('OBJ',o.name,[m.name for m in me.materials],len(me.vertices),'near',len(pts)); [print('  %.2f %.2f %.2f'%tuple(p)) for p in pts[:40]]
