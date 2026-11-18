import bpy
for n in ('WS27_CollegeAve_asphalt_2020ortho','WS27_curb_concrete_UNVERIFIED','fo_cogen_white_paint','WS3_Mulch_bark_dark_brown'): bpy.data.materials.new(n)
bpy.ops.mesh.primitive_cone_add(location=(100,90,0)); bpy.context.object.name='T_RedMaple_L1_0004'; bpy.context.object.scale=(5,5,10)
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws143/main142b.py').read())
print('TESTOK',[(o.name[:40]) for o in bpy.data.objects if o.name.startswith(('WS142','WS143'))])
