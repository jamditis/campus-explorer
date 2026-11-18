import bpy
for n in ('WS27_CollegeAve_asphalt_2020ortho','WS27_curb_concrete_UNVERIFIED','fo_cogen_white_paint'): bpy.data.materials.new(n)
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws142/main142.py').read())
print('TESTOK',[o.name[:30] for o in bpy.data.objects if o.name.startswith('WS142')])
