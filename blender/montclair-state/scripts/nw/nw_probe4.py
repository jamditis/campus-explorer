import bpy, mathutils, collections
for o in bpy.data.objects:
    if o.hide_render or o.name.startswith(('CCOM_Win_Wing_A_ceil','CCOM_east_roof_plate_z2','CCOM_east_flat_roof_clean','School of Communication and Media roof','CCOM_int_lounge_ceil','School of Communication and Media hip','el coping')): o.hide_viewport=True
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
for y in [17+0.5*i for i in range(0,22)]:
    row=[]
    for x in [-17+0.5*i for i in range(0,24)]:
        hit,loc,n,i,o,m=sc.ray_cast(dg,mathutils.Vector((x,y,142.9)),mathutils.Vector((0,0,-1)))
        c='.'
        if hit:
            mat=o.active_material.name if o.active_material else ''
            s=(o.name+mat).lower()
            c='G' if o.name.startswith('Terrain') else ('W' if o.name.startswith('NW') else ('t' if 'tower' in o.name else '?'))  if False else ('G' if o.name.startswith('Terrain') else ('W' if o.name.startswith('NW') else ('t' if 'tower' in o.name.lower() else ('N' if o.name.startswith(('NQ','NR','NV')) else ('h' if loc.z>139 else 'f'))))) ; zz=0 # else ('w' if 'wall' in s else ('N' if o.name.startswith(('NQ','NR','NV')) else ('h' if loc.z>139 else 'f')))
        row.append(c)
    print('R%5.1f '%y+''.join(row))
