import bpy, mathutils
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
from collections import Counter
for y in [x*0.5 for x in range(26,48)]:
    row=[]
    for x in [i*0.5 for i in range(-6,26)]:
        hit,loc,n,i,o,m=sc.ray_cast(dg,mathutils.Vector((x,y,141.3)),mathutils.Vector((0,0,-1)))
        row.append((o.name[:14] if o else '-')+'@%.1f'%(loc.z if hit else 0))
    print('Y%.1f|'%y,' '.join(row))
# also walls / objects bounding back hallway region at ground
def bb(o):
    cs=[o.matrix_world@mathutils.Vector(c) for c in o.bound_box]; return [round(min(c[i] for c in cs),2) for i in range(3)],[round(max(c[i] for c in cs),2) for i in range(3)]
for o in bpy.data.objects:
    if o.type=='MESH' and not o.hide_render:
        lo,hi=bb(o)
        if lo[0]<12 and hi[0]>-3 and lo[1]<23 and hi[1]>14 and lo[2]<141 and hi[2]>137 and (hi[0]-lo[0])<60:
            print('W|',o.name,lo,hi)
