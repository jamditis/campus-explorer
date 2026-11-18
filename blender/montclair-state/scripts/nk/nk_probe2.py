import bpy, mathutils
def bb(o):
    cs=[o.matrix_world@mathutils.Vector(c) for c in o.bound_box]; return [round(min(c[i] for c in cs),2) for i in range(3)],[round(max(c[i] for c in cs),2) for i in range(3)]
for o in bpy.data.objects:
    if o.type!='MESH' or o.hide_render: continue
    lo,hi=bb(o)
    if hi[0]-lo[0]>120: continue
    # overlaps the candidate room volumes
    for tag,(x0,x1,y0,y1) in (('NROOM',(-1.0,7.0,13.85,18.2)),('SROOM',(-0.5,8.0,2.8,7.15))):
        if lo[0]<x1 and hi[0]>x0 and lo[1]<y1 and hi[1]>y0 and lo[2]<141.3 and hi[2]>137.6:
            print(tag,o.name,lo,hi,[s.material.name if s.material else None for s in o.material_slots][:3],o.users_collection[0].name,len(o.data.polygons), [m.type for m in o.modifiers])
# rays along the hallway walls: what's 0.3..4m behind the door centres
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
for x in (1.0,5.0,1.5,6.0):
    for (y,dy) in ((13.0,1),(8.0,-1)):
        o=mathutils.Vector((x,y,139.0)); d=mathutils.Vector((0,dy,0))
        seq=[]; p=o.copy()
        for k in range(6):
            r=sc.ray_cast(dg,p,d,distance=8)
            if not r[0]: break
            seq.append((r[4].name,round(r[1].y,2))); p=r[1]+d*0.002
        print('RAY',x,y,dy,seq)
