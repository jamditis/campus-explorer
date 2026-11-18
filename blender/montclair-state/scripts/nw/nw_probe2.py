import bpy, mathutils, collections
for o in bpy.data.objects:
    if o.hide_render or o.name.startswith(('CCOM_Win_Wing_A_ceil','CCOM_east_roof_plate_z2','CCOM_east_flat_roof_clean','School of Communication and Media roof','CCOM_int_lounge_ceil','School of Communication and Media hip','el coping','CCOM tower')): o.hide_viewport=True
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
cnt=collections.Counter()
for y in [18+0.5*i for i in range(0,14)]:
    row=[]
    for x in [-12+0.5*i for i in range(0,30)]:
        hit,loc,n,i,o,m=sc.ray_cast(dg,mathutils.Vector((x,y,142.9)),mathutils.Vector((0,0,-1)))
        c='.'
        if hit:
            mat=o.active_material.name if o.active_material else ''
            cnt[(o.name[:60],mat[:40],round(loc.z,1))]+=1
            s=(o.name+mat).lower()
            c='G' if ('grass' in s or 'lawn' in s or 'turf' in s or o.name.startswith('Terrain')) else ('w' if 'wall' in s else ('N' if o.name.startswith(('NQ','NR','NV')) else ('h' if loc.z>139 else 'f')))
        row.append(c)
    print('R%5.1f '%y+''.join(row))
for k,v in cnt.most_common(40): print('HIT',v,k)
