import bpy, os
os.environ['SAVE']='1'
exec(open('scripts/no/no_build.py').read())
exec(open('scripts/no/no_render.py').read())
