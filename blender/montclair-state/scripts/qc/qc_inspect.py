import bpy
exec(open('scripts/qc/qc_find.py').read())
F,WT=qc_find(); print('QC_FOUND',len(F),'WT',WT)
for f in F: print('QCF',f['idx'],f['cols'],f['rows'],'u %.2f-%.2f v %.2f-%.2f'%(f['umin'],f['umax'],f['vmin'],f['vmax']),'Wu %.3f Wv %.3f ang %.3f res %.4f'%(f['Wu'].length,f['Wv'].length,f['Wu'].angle(f['Wv']),f['res']),'n',tuple(round(x,3) for x in f['n']),'c',tuple(round(x,1) for x in f['c']),'nv',f['nv'],'A %.2f'%f['area'])
for n in ('PR_Calcia_slot_surrounds_UNVERIFIED','PS_Calcia_slot_reveals_glass_UNVERIFIED'):
    o=bpy.data.objects.get(n); print(n, o and len(o.data.polygons))
w=bpy.data.objects['Calcia Hall walls']; print('mats',[m.name for m in w.data.materials],'polys',len(w.data.polygons),'attrs',[a.name for a in w.data.attributes])
