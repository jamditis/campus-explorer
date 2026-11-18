import bpy, mathutils
hide=[o for o in bpy.data.objects if o.name.startswith(('CCOM_Win_Wing_A_ceil','CCOM_east_roof_plate_z2','CCOM_east_flat_roof_clean','School of Communication and Media roof','CCOM_int_lounge_ceil'))]
for o in hide: o.hide_viewport=True
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
for y in [13+0.5*i for i in range(0,24)]:
    row=[]
    for x in [-9+0.5*i for i in range(0,48)]:
        hit,loc,n,i,o,m=sc.ray_cast(dg,mathutils.Vector((x,y,145.5)),mathutils.Vector((0,0,-1)))
        c='.' 
        if hit:
            nm=o.name
            c='G' if nm.startswith('Terrain') else ('w' if 'wall' in nm.lower() else ('f' if loc.z<138 else '^'))
        row.append(c)
    print('R%5.1f '%y+''.join(row))
