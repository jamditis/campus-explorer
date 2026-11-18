import bpy
from mathutils import Vector
ic=bpy.data.collections['OH_SCH_Win_red_frame_20261031oh']
for ob in ic.all_objects:
    bb=[Vector(c) for c in ob.bound_box]; M=ob.matrix_world
    w=[M@v for v in bb]
    print('LB',ob.name,'x',round(min(v.x for v in w),3),round(max(v.x for v in w),3),'y',round(min(v.y for v in w),3),round(max(v.y for v in w),3),'z',round(min(v.z for v in w),3),round(max(v.z for v in w),3))
print('ic offset',ic.instance_offset)
o=bpy.data.objects['SCH_win_000_r0']; print(o.matrix_world)
w=bpy.data.objects['Schmitt Hall walls']; mi=w.matrix_world.inverted()
M=o.matrix_world; c=M.translation; Y=(M.to_3x3()@Vector((0,1,0))).normalized()
for s in (1,-1):
    org=c+Y*s*1.0+Vector((0,0,0.3)); h,l,n,i=w.ray_cast(mi@org,mi.to_3x3()@(-Y*s),distance=3)
    print('ray from side',s,h,(w.matrix_world@l-c).dot(Y) if h else None)
import collections
print(collections.Counter(round(x.get('bay_u',0),2) for x in bpy.data.objects if x.name.startswith('SCH_win_')))
print(collections.Counter(tuple(round(v,3) for v in x.scale) for x in bpy.data.objects if x.name.startswith('SCH_win_')))
