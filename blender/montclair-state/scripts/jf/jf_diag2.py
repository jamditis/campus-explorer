# jf diag2: tilted faces strictly inside the aisles (|d| < AW/2), any material except base/stage; plus iy wedges.
import bpy, bmesh, math
CX,CY,AW=-167.322,0.669,1.3; ATH=(1.5911,2.2578); H=AW/2
ob=bpy.data.objects['Kasser_amphitheater_bowl_hl']; me=ob.data
names=[s.material.name if s.material else '' for s in ob.material_slots]
SKIP={names.index(n) for n in ('hn_amphi_base_fieldstone','io_amphi_stage_concrete')}
bm=bmesh.new(); bm.from_mesh(me); bm.normal_update()
CH=bm.faces.layers.int.get('jb_chamfer'); WL=bm.faces.layers.int.get('iy_wedge')
def fr(co,ai):
    a=ATH[ai]; dx,dy=co.x-CX,co.y-CY; return dx*math.cos(a)+dy*math.sin(a), -dx*math.sin(a)+dy*math.cos(a)
from collections import Counter
c=Counter(); tot=Counter(); ex=[]
for f in bm.faces:
    if f.material_index in SKIP: continue
    cc=f.calc_center_median()
    for ai in (0,1):
        s,d=fr(cc,ai)
        if s>0 and abs(d)<H-0.02 and s<40:
            n=f.normal
            if 0.12<abs(n.z)<0.95 and not f[CH]:
                c[(ai,names[f.material_index][:24],bool(WL and f[WL]))]+=1; tot[ai]+=f.calc_area()
                if ai==1 and 5<s<20: ex.append((round(s,2),round(d,2),round(cc.z,2),round(n.z,2),round(f.calc_area()*1e4,1),len(f.verts),bool(WL and f[WL])))
print('JF2',dict(c)); print('JF2 area m2',dict(tot))
for e in sorted(ex): print('JF2 ex',e)
