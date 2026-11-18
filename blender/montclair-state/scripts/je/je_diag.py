# Session je diag (read-only): list tilted / overhanging non-chamfer faces of the amphitheater bowl (aisle-cheek corner candidates).
import bpy, bmesh
ob=bpy.data.objects['Kasser_amphitheater_bowl_hl']; me=ob.data; mw=ob.matrix_world
names=[s.material.name if s.material else '' for s in ob.material_slots]
print('JED mw identity?',[list(r) for r in mw]); print('JED mats',names)
bm=bmesh.new(); bm.from_mesh(me); bm.normal_update()
L={k:bm.faces.layers.int.get(k) for k in ('jb_chamfer','iy_wedge','jc_flatn')}
print('JED layers',{k:bool(v) for k,v in L.items()}, 'faces',len(bm.faces))
cnt={}
rows=[]
for f in bm.faces:
    n=f.normal; ch=f[L['jb_chamfer']] if L['jb_chamfer'] else 0; w=f[L['iy_wedge']] if L['iy_wedge'] else 0
    if names[f.material_index]=='hn_amphi_base_fieldstone': continue
    tilt = 0.15<abs(n.z)<0.9
    if (tilt and not ch) or w or n.z<-0.05:
        c=mw@f.calc_center_median()
        rows.append((round(c.x,2),round(c.y,2),round(c.z,2),[round(x,2) for x in n],round(f.calc_area()*1e4,1),len(f.verts),names[f.material_index][:22],'ch',ch,'w',w))
rows.sort()
for r in rows: print('JED',*r)
print('JED total',len(rows))
# chamfer normal stats
import collections
h=collections.Counter(round(f.normal.z,1) for f in bm.faces if L['jb_chamfer'] and f[L['jb_chamfer']])
print('JED chamfer nz hist',sorted(h.items()))
