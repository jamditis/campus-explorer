import bpy
with bpy.data.libraries.load('north/montclair_north.blend') as (a,b):
    cs=[c for c in a.collections if 'tudent' in c or 'SC_' in c or 'Annex' in c]
print('NORTH_COLS',cs)
print('MAIN_OBJS',[ (o.name,o.hide_render) for o in bpy.data.objects if 'Student Center' in o.name or o.name.startswith('SC')][:40])
