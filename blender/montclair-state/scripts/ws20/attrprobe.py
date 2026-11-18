import bpy
me=bpy.data.objects['Life Hall walls'].data
for a in me.attributes:
    if a.name.startswith('.'): continue
    vals=[d.value for d in a.data] if hasattr(a.data[0],'value') else None
    print('A',a.name,a.domain,a.data_type, (round(min(vals),2),round(max(vals),2),len(set(round(x,2) for x in vals))) if vals else '')
