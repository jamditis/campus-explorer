import bpy, os
os.environ['SAVE']='1'
exec(open('scripts/nk/nk_build.py').read())
exec(open('scripts/nk/nk_render.py').read())
