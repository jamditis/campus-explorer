import bpy, os
for n in os.environ.get('OFF','').split(','):
    if n: bpy.data.objects[n].hide_render=True; print('OFF',n)
exec(open('scripts/nt/nt_render.py').read())
