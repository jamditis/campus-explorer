import bpy
wo=bpy.data.objects['Schmitt Hall walls']
print({k:wo[k] for k in wo.keys() if not k.startswith('_')})
print([u.name for u in wo.data.uv_layers], len(wo.data.polygons))
m=wo.data.materials[0]; print(m.name, m.users)
print(bpy.data.libraries.get('windows_ccom.blend'))
import bpy
with bpy.data.libraries.load('/workspace/nj-scenes/assets/windows_ccom.blend', link=True) as (s,d): print(s.collections)
for nm in ('CCOM_Win_Wing_A',):
    c=bpy.data.collections.get(nm); print(nm, c and dict(c.items()))
