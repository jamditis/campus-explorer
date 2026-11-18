import bpy, mathutils, collections
for o in bpy.data.objects:
    if o.hide_render or o.name.startswith(('CCOM_Win_Wing_A_ceil','CCOM_east_roof_plate_z2','CCOM_east_flat_roof_clean','School of Communication and Media roof','CCOM_int_lounge_ceil','School of Communication and Media hip','el coping','CCOM tower')): o.hide_viewport=True
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
for y in [14+0.5*i for i in range(0,26)]:
    row=[]
    for x in [-22+0.5*i for i in range(0,44)]:
        hit,loc,n,i,o,m=sc.ray_cast(dg,mathutils.Vector((x,y,142.9)),mathutils.Vector((0,0,-1)))
        c='.'
        if hit:
            mat=o.active_material.name if o.active_material else ''
            s=(o.name+mat).lower()
            c='G' if o.name.startswith('Terrain') else ('w' if 'wall' in s else ('N' if o.name.startswith(('NQ','NR','NV')) else ('h' if loc.z>139 else 'f')))
        row.append(c)
    print('R%5.1f '%y+''.join(row))
def bb(o):
    cs=[o.matrix_world@mathutils.Vector(c) for c in o.bound_box]; return [min(c[i] for c in cs) for i in range(3)],[max(c[i] for c in cs) for i in range(3)]
for P in [(-6,18.3,139),(-6,19.3,138),(-11.8,21,138),(-15,19.3,138)]:
    for o in bpy.data.objects:
        if o.type!='MESH' or o.hide_render: continue
        lo,hi=bb(o)
        if all(lo[i]-0.05<=P[i]<=hi[i]+0.05 for i in range(3)) and (hi[0]-lo[0])<40: print('AT',P,o.name[:70],[round(a,2) for a in lo],[round(a,2) for a in hi])
