import bpy, hashlib
objs=sorted(o.name for o in bpy.data.objects)
print('OBJS', len(objs))
print('FINLEY_TOP', max((bpy.data.objects['Finley Hall walls'].matrix_world@v.co).z for v in bpy.data.objects['Finley Hall walls'].data.vertices))
print('FREEMAN_TOP', max((bpy.data.objects['Freeman Hall walls'].matrix_world@v.co).z for v in bpy.data.objects['Freeman Hall walls'].data.vertices))
print('UB', bpy.data.objects['Freeman Hall walls'].get('ub_fix'))
