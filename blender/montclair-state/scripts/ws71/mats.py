import bpy
print('M71',[m.name for m in bpy.data.materials if any(k in m.name.lower() for k in ('mulch','bed','plant','concrete','walk'))][:60])
print('M71o',[o.name for o in bpy.data.objects if any(k in o.name.lower() for k in ('mulch','shrub','hedge'))][:30])
