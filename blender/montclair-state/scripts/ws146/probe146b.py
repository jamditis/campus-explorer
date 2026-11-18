
import bpy, mathutils
for ob in bpy.data.objects:
    if ob.type!='MESH': continue
    bb=[ob.matrix_world @ mathutils.Vector(c) for c in ob.bound_box]
    xs=[v.x for v in bb]; ys=[v.y for v in bb]; zs=[v.z for v in bb]
    if max(xs)<-80 or min(xs)>-60 or max(ys)<-186 or min(ys)>-166: continue
    if (max(xs)-min(xs))>150: continue
    mats=",".join(s.material.name for s in ob.material_slots if s.material)[:90]
    print("OB",ob.name[:60],"x%.0f..%.0f y%.0f..%.0f z%.2f..%.2f"%(min(xs),max(xs),min(ys),max(ys),min(zs),max(zs)),"hide" if ob.hide_render else "", mats)
