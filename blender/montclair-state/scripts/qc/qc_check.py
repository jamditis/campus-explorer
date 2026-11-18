import bpy
o=bpy.data.objects['Calcia Hall walls']; me=o.data; uv=me.uv_layers['facade'].data; mw=o.matrix_world
for p in me.polygons:
    us=[uv[l].uv[0] for l in p.loop_indices]; vv=[uv[l].uv[1] for l in p.loop_indices]
    if max(us)>89.3 and min(us)<91.3 and abs(p.normal.z)<0.3:
        print('W',p.index,'u %.2f-%.2f v %.2f-%.2f'%(min(us),max(us),min(vv),max(vv)),'mi',p.material_index,'n',tuple(round(x,2) for x in p.normal),'nv',len(us),'zc %.1f'%(mw@p.center).z)
