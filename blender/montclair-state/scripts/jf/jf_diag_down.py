# jf: list down-facing (n.z<-0.05) non-base/stage faces with neighbours' materials
import bpy, bmesh, math
ob=bpy.data.objects['Kasser_amphitheater_bowl_hl']; me=ob.data
names=[s.material.name if s.material else '' for s in ob.material_slots]
SKIP={names.index(n) for n in ('hn_amphi_base_fieldstone','io_amphi_stage_concrete')}
bm=bmesh.new(); bm.from_mesh(me); bm.normal_update(); CH=bm.faces.layers.int.get('jb_chamfer')
for f in bm.faces:
    if f.normal.z<-0.05 and f.material_index not in SKIP:
        print('JFD',f.index,names[f.material_index][:20],'ch',f[CH],'c',[round(x,2) for x in f.calc_center_median()],'A cm2',round(f.calc_area()*1e4,1),'n',[round(x,2) for x in f.normal],'vz',[round(v.co.z,3) for v in f.verts])
