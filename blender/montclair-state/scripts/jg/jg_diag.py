# Session jg diag (read-only): battered riser faces left after jf, split by row-0 stage-front vs others; foot-vert link classes; counts.
import bpy, bmesh, math
from collections import Counter
CX,CY,AW=-167.322,0.669,1.3; ATH=(1.5911,2.2578); H=AW/2
ob=bpy.data.objects['Kasser_amphitheater_bowl_hl']; me=ob.data
names=[s.material.name if s.material else '' for s in ob.material_slots]
SKIP={names.index(n) for n in ('hn_amphi_base_fieldstone','io_amphi_stage_concrete')}
AIS={i for i,n in enumerate(names) if 'aisle' in n}; RIS=names.index('hn_amphi_riser_coursed_stone')
bm=bmesh.new(); bm.from_mesh(me); bm.normal_update()
CH=bm.faces.layers.int.get('jb_chamfer'); WL=bm.faces.layers.int.get('iy_wedge')
def batt(f): return f.material_index==RIS and not f[CH] and 0.12<f.normal.z<0.6
B=[f for f in bm.faces if batt(f)]
r0=[f for f in B if min(v.co.z for v in f.verts)<132.6]
print('JGD names',names)
print('JGD batt',len(B),'row0',len(r0),'area row0 %.1f other %.1f'%(sum(f.calc_area() for f in r0),sum(f.calc_area() for f in B if f not in r0)))
zs=[min(v.co.z for v in f.verts) for f in r0]; zt=[max(v.co.z for v in f.verts) for f in r0]
if r0: print('JGD row0 zb %.3f-%.3f zt %.3f-%.3f'%(min(zs),max(zs),min(zt),max(zt)), 'nz', round(min(f.normal.z for f in r0),2), round(max(f.normal.z for f in r0),2))
c=Counter()
for f in r0:
    zb=min(v.co.z for v in f.verts)
    for v in f.verts:
        if v.co.z<zb+0.03:
            c[(v.is_boundary, tuple(sorted(set(names[g.material_index][:18] for g in v.link_faces))))]+=1
for k,n in c.most_common(12): print('JGD r0foot',n,k)
c2=Counter()
for f in B:
    if f in r0: continue
    zb=min(v.co.z for v in f.verts)
    for v in f.verts:
        if v.co.z<zb+0.03: c2[(v.is_boundary, tuple(sorted(set(names[g.material_index][:18] for g in v.link_faces))))]+=1
for k,n in c2.most_common(12): print('JGD otherfoot',n,k)
print('JGD wedges',sum(1 for f in bm.faces if WL and f[WL]),'down',sum(1 for f in bm.faces if f.normal.z<-0.05 and f.material_index not in SKIP and f.calc_area()>2e-4),'nm',sum(1 for e in bm.edges if len(e.link_faces)>2),'bnd',sum(1 for e in bm.edges if e.is_boundary),'faces',len(bm.faces))
