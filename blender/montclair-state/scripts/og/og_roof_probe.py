import bpy, collections
o=bpy.data.objects['Schmitt Hall roof (LiDAR)']; me=o.data
print([m.name for m in me.materials])
st=collections.Counter()
for f in me.polygons:
    nz=round(f.normal.z,1); st[(f.material_index,nz, len(f.vertices))]+=1
for k,v in sorted(st.items()): print(k,v)
