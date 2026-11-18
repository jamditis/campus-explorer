import bpy, bmesh, numpy as np
ob=bpy.data.objects['Kasser_amphitheater_bowl_hl']; me=ob.data
names=[s.material.name if s.material else '' for s in ob.material_slots]
bm=bmesh.new(); bm.from_mesh(me); bm.normal_update(); bm.faces.ensure_lookup_table()
lay=bm.faces.layers.int.get('jb_chamfer')
res=[]
for f in bm.faces:
    if len(f.verts)>3 and abs(f.normal.z)<0.5:
        d=max(abs((v.co-f.calc_center_median()).dot(f.normal)) for v in f.verts)
        if d>0.004: res.append((d,f))
res.sort(key=lambda t:-t[0]); print('JC3 nonplanar vt faces >4mm',len(res), 'by mat',{n:sum(1 for d,f in res if names[f.material_index]==n) for n in names})
for d,f in res[:10]:
    print('JC3',f.index,round(d*1000,1),'mm',names[f.material_index][:24],'ch',f[lay],'nv',len(f.verts),'A',round(f.calc_area()*1e4,1),[tuple(round(c,3) for c in v.co) for v in f.verts])
