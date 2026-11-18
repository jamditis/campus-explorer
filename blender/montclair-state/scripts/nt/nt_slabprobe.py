import bpy, mathutils
def bb(o):
    cs=[o.matrix_world@mathutils.Vector(c) for c in o.bound_box]; return [round(min(c[i] for c in cs),2) for i in range(3)],[round(max(c[i] for c in cs),2) for i in range(3)]
for o in bpy.data.objects:
    if o.type!='MESH' or o.hide_render: continue
    lo,hi=bb(o)
    if hi[0]>-21 and lo[0]<16 and hi[1]>-14 and lo[1]<28 and hi[2]>140.0 and hi[2]<146.2 and (hi[0]-lo[0])*(hi[1]-lo[1])>6:
        print('S|',o.name,'|',lo,hi,len(o.data.vertices),o.users_collection[0].name if o.users_collection else '')
for n in ('NS_CAM_aerial_cutaway_studio_atrium_oblique','NS_CAM_eye_1F_open_floor_cafe_looking_east','NS_CAM_eye_atrium_looking_west_to_doors'):
    o=bpy.data.objects[n]; print('C|',n,tuple(round(v,2) for v in o.location),tuple(round(v,3) for v in o.rotation_euler),o.data.lens)
