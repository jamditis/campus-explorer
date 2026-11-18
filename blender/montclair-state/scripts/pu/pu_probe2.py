import bpy, collections
r=bpy.data.objects['Dickson Hall roof (LiDAR)']; me=r.data; mw=r.matrix_world
print('RSLOTS',[(i,s.link,s.material.name if s.material else None) for i,s in enumerate(r.material_slots)])
print('MESHMATS',[m.name if m else None for m in me.materials])
c=collections.Counter(); zs=[]
for p in me.polygons:
    n=mw.to_3x3()@p.normal
    if abs(n.normalized().z)<0.35: c[p.material_index]+=1; zs.append((mw@p.center).z)
print('STEEP by mi',c, 'z',min(zs),max(zs),'n',len(zs))
for nm in ('North_Dickson_brick_buff_plain','PE_Dickson_coping_dark_bronze_UNVERIFIED'): print(nm, nm in bpy.data.materials)
for o in bpy.data.objects:
    if o.name.startswith(('ek coping caps Dickson','el coping strips Dickson')): print('COP',o.name,len(o.data.polygons),[m.name for m in o.data.materials],o.hide_render)
