import bpy
for n in ('WS27_CollegeAve_asphalt_2020ortho','WS27_curb_concrete_UNVERIFIED','fo_cogen_white_paint'): bpy.data.materials.new(n)
import os; os.environ['OUT']=''
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws143/main142b.py').read())
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws145/nose145.py').read())
print('TESTOK',[(o.name[:44],len(o.data.polygons)) for o in bpy.data.objects if o.name.startswith(('WS142','WS143','WS145'))])
