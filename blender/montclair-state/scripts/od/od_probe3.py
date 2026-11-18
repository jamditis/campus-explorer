import bpy
o=bpy.data.objects['NG atrium wide stair wood clad']; me=o.data
for p in me.polygons:
    vs=[me.vertices[i].co for i in p.vertices]
    if p.material_index==1 or abs(p.normal.z)>0.9:
        print('F',p.material_index,[round(p.normal[k],2) for k in range(3)],round(min(v.x for v in vs),3),round(max(v.x for v in vs),3),round(min(v.y for v in vs),2),round(max(v.y for v in vs),2),round(min(v.z for v in vs),3),round(max(v.z for v in vs),3))
