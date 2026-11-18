import bpy
print('COLS',[c.name for c in bpy.data.collections if c.name.startswith('NZ')])
obs=[o for o in bpy.data.objects if o.name.startswith('NZ')]
print('NZOBJ',len(obs),[ (o.name,[c.name for c in o.users_collection]) for o in obs][:3])
print('TOTAL',len(bpy.data.objects))
