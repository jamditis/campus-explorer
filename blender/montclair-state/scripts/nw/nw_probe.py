import bpy, mathutils, collections
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
cnt=collections.Counter()
for y in [18+0.5*i for i in range(0,12)]:
    row=[]
    for x in [-12+0.5*i for i in range(0,28)]:
        hit,loc,n,i,o,m=sc.ray_cast(dg,mathutils.Vector((x,y,190)),mathutils.Vector((0,0,-1)))
        c='.'
        if hit:
            mat=o.active_material.name if o.active_material else ''
            cnt[(o.name[:60],mat[:40],round(loc.z,1))]+=1
            g='grass' in (o.name+mat).lower() or 'lawn' in (o.name+mat).lower() or 'turf' in (o.name+mat).lower()
            c='G' if g else ('T' if o.name.startswith('Terrain') else ('r' if loc.z>150 else ('h' if loc.z>139 else 'f')))
        row.append(c)
    print('R%5.1f '%y+''.join(row))
for k,v in cnt.most_common(40): print('HIT',v,k)
# NQ fill boxes near
for o in bpy.data.objects:
    if o.type=='MESH':
        cs=[o.matrix_world@mathutils.Vector(c) for c in o.bound_box]
        lo=[min(c[i] for c in cs) for i in range(3)]; hi=[max(c[i] for c in cs) for i in range(3)]
        if hi[0]>-10 and lo[0]<0 and hi[1]>19.5 and lo[1]<22 and lo[2]<150 and hi[0]-lo[0]<60:
            print('OBJ',o.name[:70],[round(a,2) for a in lo],[round(a,2) for a in hi],o.hide_render, o.get('msu_area'))
