import bpy, json
o=bpy.data.objects['Schmitt Hall roof (LiDAR)']; me=o.data; mw=o.matrix_world
out=[]
for f in me.polygons:
    if f.material_index!=0: continue
    c=mw@f.center; out.append([round(c.x,2),round(c.y,2),round(c.z,3),round(f.normal.z,3),round(f.area,3)])
json.dump(out,open('data/og/schmitt_roof_faces.json','w'))
print('dumped',len(out))
