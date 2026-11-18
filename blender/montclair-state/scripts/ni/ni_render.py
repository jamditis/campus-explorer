import bpy, os
exec(open('scripts/ni/ni_build.py').read()) if os.environ.get('BUILD')=='1' else None
