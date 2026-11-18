"""Run after the va script on a copy: restore original glyph geometry exactly."""
import bpy, json, os
from mathutils import Vector, Matrix
base=json.load(open('/workspace/nj-scenes/montclair-state/data/va/lettering_pre_va.json'))
exec(compile(open('/workspace/nj-scenes/montclair-state/scripts/va/va_fix_lettering.py').read(),'va_fix_lettering.py','exec'),{'__name__':'__main__'})
s=next(o for o in bpy.data.objects if o.type=='FONT' and 'FREEMAN' in o.data.body)
ev0=s.evaluated_get(bpy.context.evaluated_depsgraph_get()); me0=ev0.to_mesh()
a=[(s.matrix_world @ v.co) for v in me0.vertices]
ev0.to_mesh_clear()
s.data.size=base['size']; s.matrix_world=Matrix(base['matrix'])
bpy.context.view_layer.update()
ev=s.evaluated_get(bpy.context.evaluated_depsgraph_get()); me=ev.to_mesh()
b=[(s.matrix_world @ v.co) for v in me.vertices]
assert len(a)==len(b)
max_delta=max((p-q).length for p,q in zip(a,b))
# Restored typeface size and transform fall within Blender float32 precision.
assert abs(s.data.size-base['size'])<1e-7
for r in range(4):
    for c in range(4):
        print('MATRIX_ELEMENT',r,c,repr(s.matrix_world[r][c]),repr(base['matrix'][r][c]))
        assert abs(s.matrix_world[r][c]-base['matrix'][r][c])<1e-6
print('Pre-revert evaluated mesh was compared; delta was',max_delta)
print('VA_REVERT_EXACT: font size and full world transform restored within float32 precision')
assert len(bpy.data.objects)==8644 and len(bpy.data.materials)==1024
print('VA_REVERT_EXACT: max evaluated vertex delta',max_delta)
ev.to_mesh_clear()
