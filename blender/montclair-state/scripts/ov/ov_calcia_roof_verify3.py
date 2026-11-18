import bpy
r=bpy.data.objects['Calcia Hall roof (LiDAR)']; me=r.data
tot=sum(p.area for p in me.polygons if p.material_index==0)
for t in (0.93,0.95,0.97,0.985):
    print('NZ<',t,round(sum(p.area for p in me.polygons if p.material_index==0 and p.normal.z<t)/tot,3))
print('smooth faces frac',round(sum(1 for p in me.polygons if p.use_smooth)/len(me.polygons),3))
me.calc_normals_split() if hasattr(me,'calc_normals_split') else None
cn=[c.vector.z for c in me.corner_normals] if hasattr(me,'corner_normals') else []
if cn: print('corner nz<0.985 frac',round(sum(1 for z in cn if z<0.985)/len(cn),3),'<0.95',round(sum(1 for z in cn if z<0.95)/len(cn),3))
d=bpy.data.objects['Dickson Hall roof (LiDAR)'].data; td=sum(p.area for p in d.polygons if p.material_index==0)
print('DICKSON NZ<0.985',round(sum(p.area for p in d.polygons if p.material_index==0 and p.normal.z<0.985)/td,3))
