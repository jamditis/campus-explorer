import bpy
from mathutils import Vector
o=bpy.data.objects['Calcia Hall walls']; me=o.data; uv=me.uv_layers['facade'].data; mw=o.matrix_world
ps=bpy.data.objects['PS_Calcia_slot_reveals_glass_UNVERIFIED']; pm=ps.data
gl=[ps.matrix_world@p.center for p in pm.polygons if p.material_index==1]
for k in (5,36,37,47):
    u0=2.4*k+0.75; u1=u0+0.9
    print('COL',k,u0,u1)
    for p in me.polygons:
        if abs(p.normal.z)>0.3: continue
        us=[uv[l].uv[0] for l in p.loop_indices]; vv=[uv[l].uv[1] for l in p.loop_indices]
        if max(us)>u0+0.02 and min(us)<u1-0.02:
            c=mw@p.center
            print('  F',p.index,'u %.2f-%.2f v %.2f-%.2f'%(min(us),max(us),min(vv),max(vv)),'mi',p.material_index,'n',tuple(round(x,2) for x in p.normal),'c',tuple(round(x,1) for x in c))
    # glass near
    F=[p for p in me.polygons if abs(p.normal.z)<0.3 and min(uv[l].uv[0] for l in p.loop_indices)<=u0 and max(uv[l].uv[0] for l in p.loop_indices)>=u1]
    for p in F[:1]:
        c=mw@p.center
        near=[g for g in gl if (Vector((g.x,g.y))-Vector((c.x,c.y))).length<1.5]
        print('  PSglass near',[tuple(round(x,1) for x in g) for g in near])
