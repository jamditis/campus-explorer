import bpy
for o in bpy.data.objects:
    if o.name.startswith(('TL_tree_095','TL_tree_099','TL_tree_100','TL_tree_096')): o.hide_render=True
exec(open('scripts/wc/wc_render.py').read())
